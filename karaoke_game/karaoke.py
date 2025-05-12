# read MIDI
#   convert to frequencies
#   save before we play, to add timing buffer even before the tone
#   play MIDI
# detect Audio (detect loudest frequency)
# Compare MIDI and main input frequency (timing and frequency)
# Show, how the relation is (i.e. 10Hz off, too early, too late)

import read_midi
import pygame.midi, mido
import time, threading, sys

SONG_MIDI_PATH = 'Songs/freude.mid'
TIMING_DEVIATION_TOLERANCE = 100 # in ms
TIMING_RECOGNITION_TOLERANCE = 100 # in ms
FREQUENCY_DEVIATION_TOLERANCE = 3 # in Hz

song = []
prepared_song = []
note_starts = []
note_ends = []
song_notes_to_sing = []
sung_note = 261
score = 0

game_state = "start"

def main():
    prepare_song()

def prepare_song():
    global song, prepared_song, note_starts, note_ends
    song = read_midi.midi_to_timecoded_frequencies(SONG_MIDI_PATH)
    prepared_song = add_note_id(song)
    note_starts = add_time_to_next_note_start(prepared_song)
    note_ends = add_time_to_next_note_end(prepared_song)
    play_song()

def add_note_id(song):
    song_with_note_ids = []
    for id in range(len(song)):
        start, end, freq = song[id]
        song_with_note_ids.append((id, start, end, freq))

    return song_with_note_ids

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

def play_song():
    global game_state

    game_state = "play"

    add_thread = threading.Thread(target = add_notes_to_sing)
    remove_thread = threading.Thread(target = remove_notes_to_sing)
    midi_thread = threading.Thread(target = play_midi_file)
    evaluation_thread = threading.Thread(target = evaluate_audio_input)

    midi_thread.start()
    add_thread.start()
    remove_thread.start()
    evaluation_thread.start()

    exit_threads()

    add_thread.join()
    remove_thread.join()
    midi_thread.join()
    evaluation_thread.join()

def add_notes_to_sing():
    start_time = time.time()
    for note in note_starts:
        if game_state != "play":
            return
        while time.time() - start_time < note[1]:
            time.sleep(0.0001)
        song_notes_to_sing.append(note)
        print(f"START: {note}")

def remove_notes_to_sing():
    global game_state
    while game_state == "play":

        start_time = time.time()
        for note in note_ends:
            if game_state != "play":
                return
            while time.time() - start_time < note[1]:
                time.sleep(0.0001)
            matching_note = next((n for n in song_notes_to_sing if n[0] == note[0]), None)
            if matching_note:
                song_notes_to_sing.remove(matching_note)
                #print(f"END: {note}")
        game_state = "end"
        print("PROZENT RICHTIG: " + str(score / note_ends[len(note_ends) - 1][1]))

def play_midi_file():
    pygame.midi.init()
    player = pygame.midi.Output(0)
    midi_file = mido.MidiFile(SONG_MIDI_PATH)
    current_time = 0

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

def evaluate_audio_input():
    global score

    while game_state == "play":
        matching_note = next((n for n in song_notes_to_sing if abs(n[2] - sung_note) <= FREQUENCY_DEVIATION_TOLERANCE), None)
        if matching_note:
            score += 1
            print(score)
        time.sleep(0.01)

def exit_threads():
    global game_state

    while game_state == "play":
        try:
            if game_state != "play":
                break

        except KeyboardInterrupt:
            print("Abbruch")
            game_state = "exit"
            sys.exit()


if __name__ == "__main__":
    main()
