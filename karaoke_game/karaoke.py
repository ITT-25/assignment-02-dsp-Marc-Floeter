import pyglet, pygame.midi, mido
from pyglet import window, shapes
import time, threading, os
import read_midi, audio_sample

FREQUENCY_DEVIATION_TOLERANCE = 3 # Um wie viel Hz darf man den Ton verfehlen, sodass er dennoch als korrekt gezählt wird?

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_PADDING_Y = 40
FRAMERATE = 60

PLAYER_START_POS_Y = WINDOW_HEIGHT / 2
PLAYER_PADDING_X = 10
PLAYER_COLOR = (0, 0, 255)

NOTE_SPEED = 60 # in px pro Sekunde
NOTES_Y_DISTANCE_AT_START = WINDOW_WIDTH
NOTE_COLOR = (255, 0, 0)

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

player = None
note_bars = []
batch = pyglet.graphics.Batch() # Grafik-Batch zum gemeinsamen Rendern von Player und Note-Bars

song_midi_file_path = ""
song = []
note_starts = []
note_ends = []

pixel_per_hertz = 0
player_and_note_bar_height = 0
min_song_frequency = 0

song_notes_to_sing = []

score = 0
score_label = pyglet.text.Label("Score:", x = WINDOW_WIDTH/2, y = WINDOW_HEIGHT - WINDOW_PADDING_Y, anchor_x = "center", anchor_y = "center", font_size = 20)

game_state = "choose_midi"


class Player:
    def __init__(self):
        self.x = PLAYER_PADDING_X
        self.y = PLAYER_START_POS_Y
        self.sprite = shapes.Rectangle(self.x, self.y, player_and_note_bar_height, player_and_note_bar_height, PLAYER_COLOR, batch = batch)

class Note_Bar:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.sprite = shapes.Rectangle(self.x, self.y, self.width, player_and_note_bar_height, NOTE_COLOR, batch = batch) 


def main():
    input_midi_file()
    init_visuals()
    prepare_song()
    play_song()


def input_midi_file():
    global song_midi_file_path, song

    # MIDI-File Input Dialog
    song_midi_file_path = input("Pfad zu MIDI: ")
    if not os.path.exists(song_midi_file_path) and not song_midi_file_path.lower().endswith(".mid"):
        print("Pfad existiert nicht oder keine MIDI-Datei!")
        input_midi_file()
    else:
        song = read_midi.midi_to_timecoded_frequencies(song_midi_file_path) # Song zuweisen, falls Pfad und Datei valide


def init_visuals():
    global player

    calculate_visual_parameters()
    player = Player()
    generate_note_bars()


def calculate_visual_parameters():
    global pixel_per_hertz, player_and_note_bar_height, min_song_frequency

    # MIN und MAX Frequenzen des Songs berechnen
    current_min_freq = 99999999999
    current_max_freq = 0
    for note in range(len(song)):
        start, end, freq = song[note]
        if freq > current_max_freq:
            current_max_freq = freq
        elif freq < current_min_freq and freq != 0: # Null = Stille
            current_min_freq = freq
    max_song_frequency = current_max_freq
    min_song_frequency = current_min_freq

    song_frequency_range = max_song_frequency - min_song_frequency

    pixel_per_hertz = (WINDOW_HEIGHT - WINDOW_PADDING_Y * 2) / song_frequency_range # Wie viele Pixel entsprechen einem Hz in dem Rahmen, in dem Noten angezeigt werden sollen
    player_and_note_bar_height = FREQUENCY_DEVIATION_TOLERANCE * 2 * pixel_per_hertz # Note Bars repräsentieren durch ihre Höhe die Frequenztoleranz (wie weit man daneben liegen darf, damit es dennoch zählt)

# Note Bars schon vor Spielstart erstellen (danach nur noch bewegen)
def generate_note_bars():
    for note in range(len(song)):
        start_time, end_time, frequency = song[note]
        note_x = start_time * NOTE_SPEED + NOTES_Y_DISTANCE_AT_START # Alle Noten anfangs rechts außerhalb des Bilds
        note_y = get_y_pos_by_frequency(frequency)
        note_width = (end_time - start_time) * NOTE_SPEED # Breite der Note = Dauer der Note * Geschwindigkeit
        note_bars.append(Note_Bar(note_x, note_y, note_width))


def get_y_pos_by_frequency(frequency):
    return (frequency - min_song_frequency) * pixel_per_hertz + WINDOW_PADDING_Y - FREQUENCY_DEVIATION_TOLERANCE


# Bereitet Song und Listen mit Noten vor, sodass sie während des Spiels korrekt mit dem Audio-Input verglichen werden können
def prepare_song():
    global song, note_starts, note_ends

    song_with_note_ids = add_note_id(song)
    note_starts = add_time_to_next_note_start(song_with_note_ids) 
    note_ends = add_time_to_next_note_end(song_with_note_ids)


# Fügt jeder Note eine ID hinzu, damit genau diese ausfindig zu machen ist, wenn man sie löschen möchte (siehe remove_notes_to_sing())
def add_note_id(song):
    song_with_note_ids = []
    for id in range(len(song)):
        start, end, freq = song[id]
        song_with_note_ids.append((id, start, end, freq))

    return song_with_note_ids


# Erstellt Liste bestehend aus nur den Noten-Startzeitpunkten inkl. der Dauer bis zum Start der nächsten Note
def add_time_to_next_note_start(song):
    song_with_time_to_next_note_start = []
    for i in range(len(song)):
        id, start, end, freq = song[i]
        if i < len(song) - 1:
            next_start = song[i + 1][1]
            time_to_next_note_start = next_start - start
        else:
            time_to_next_note_start = None 
        song_with_time_to_next_note_start.append((id, start, freq, time_to_next_note_start))
    return song_with_time_to_next_note_start


 # Siehe darüber, nur mit Noten-Endzeitpunkten
def add_time_to_next_note_end(song):
    song_sorted_by_note_end = sorted(song, key=lambda n: n[2])
    song_with_time_to_next_note_end = []
    for i in range(len(song_sorted_by_note_end)):
        id, start, end, freq = song_sorted_by_note_end[i]
        if i < len(song_sorted_by_note_end) - 1:
            next_end = song_sorted_by_note_end[i + 1][2]
            time_to_next_note_end = next_end - end
        else:
            time_to_next_note_end = None 
        song_with_time_to_next_note_end.append((id, end, time_to_next_note_end))
    return song_with_time_to_next_note_end


# Startet Threads und Schedules für parallele Spielabläufe
def play_song():
    global game_state

    game_state = "play"

    pyglet.clock.schedule_interval(process_audio_input, 1/FRAMERATE)
    pyglet.clock.schedule_interval(move_note_bars, 1/FRAMERATE)
    threading.Thread(target = add_notes_to_sing, daemon=True).start()
    threading.Thread(target = remove_notes_to_sing, daemon=True).start()
    threading.Thread(target = play_midi_file, daemon=True).start()

    pyglet.app.run()


# Füge Note zur Liste der aktuell validen hinzu
def add_notes_to_sing():
    time.sleep((NOTES_Y_DISTANCE_AT_START - PLAYER_PADDING_X - player_and_note_bar_height)/NOTE_SPEED) # Warte bis Note Bars an Grundlinie des Players angekommen sind
    start_time = time.time()
    for note in note_starts: # Iteriere alle Noten-Startzeitpunkte
        if game_state != "play":
            return
        while time.time() - start_time < note[1]: # Warte, bis nächster Startzeitpunkt erreicht
            time.sleep(0.0001)
        song_notes_to_sing.append(note) # Füge Note zur Liste der aktuell validen hinzu


# Siehe add_notes_to_sing, aber entfernt Noten aus Liste der aktuell validen
def remove_notes_to_sing(): 
    global game_state
    time.sleep((NOTES_Y_DISTANCE_AT_START - PLAYER_PADDING_X - player_and_note_bar_height)/NOTE_SPEED) # Warte bis Note Bars an Grundlinie des Players angekommen sind
    start_time = time.time()
    for note in note_ends:
        if game_state != "play":
            return
        while time.time() - start_time < note[1]:
            time.sleep(0.0001)
        matching_note = next((n for n in song_notes_to_sing if n[0] == note[0]), None)
        if matching_note:
            song_notes_to_sing.remove(matching_note)

    game_state = "end"


# Spielt Midi-Datei ab
def play_midi_file():
    pygame.midi.init()
    player = pygame.midi.Output(0)
    midi_file = mido.MidiFile(song_midi_file_path)
    current_time = 0

    time.sleep((NOTES_Y_DISTANCE_AT_START - PLAYER_PADDING_X - player_and_note_bar_height)/NOTE_SPEED) # Warte bis Note Bars an Grundlinie des Players angekommen sind
    for msg in midi_file:
        if game_state != "play":
            return
        current_time += msg.time
        time.sleep(msg.time)

        if msg.type == 'note_on' and msg.velocity > 0:
            player.note_on(msg.note, msg.velocity)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            player.note_off(msg.note, 0)

    player.close()
    pygame.midi.quit()


# Registriert und verwertet Audioinput
def process_audio_input(dt):
    input_frequency = audio_sample.get_audio_signal() # Aktuell dominante Frequenz aus Mikro holen
    player.sprite.y = get_y_pos_by_frequency(input_frequency) # Player x-Position setzen
    evaluate_audio_input(dt, input_frequency)


# Analysiert gesungene Note im Vergleich zu zu singender Note und bewertet
def evaluate_audio_input(dt, input_frequency):
    global score

    matching_note = next((n for n in song_notes_to_sing if abs(n[2] - input_frequency) <= FREQUENCY_DEVIATION_TOLERANCE), None) 
    if matching_note: # Ist die gesungene Frequenz eine aktuell zu singende Note?
        score += dt # score = wie viele Sekunden man einen richtigen Ton (oder Pause) getroffen hat


def move_note_bars(dt):
    for bar in range(len(note_bars)):
        note_bars[bar].sprite.x -= dt * NOTE_SPEED


@win.event
def on_draw():
    win.clear()
    batch.draw()
    if note_ends:
        score_label.text = "Score: " + str(round(score / note_ends[len(note_ends) - 1][1] * 100, 1)) + "%"
        score_label.draw()


if __name__ == "__main__":
    main()
