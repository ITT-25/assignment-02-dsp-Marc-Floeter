# read MIDI
#   convert to frequencies
#   save before we play, to add timing buffer even before the tone
#   play MIDI
# detect Audio (detect loudest frequency)
# Compare MIDI and main input frequency (timing and frequency)
# Show, how the relation is (i.e. 10Hz off, too early, too late)

import read_midi
import pygame.midi, mido
import time, threading

SONG_MIDI_PATH = 'Songs/freude.mid'
TIMING_DEVIATION_TOLERANCE = 100 # in ms
TIMING_RECOGNITION_TOLERANCE = 100 # in ms
FREQUENCY_DEVIATION_TOLERANCE = 3 # in Hz

song = []
prepared_song = []
note_starts = []
note_ends = []
song_notes_to_sing = []
song_notes_too_early = []
song_notes_too_late = [] 

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
    add_thread = threading.Thread(target = add_notes_to_sing)
    remove_thread = threading.Thread(target = remove_notes_to_sing)
    midi_thread = threading.Thread(target = play_midi_file)

    midi_thread.start()
    add_thread.start()
    remove_thread.start()

    add_thread.join()
    remove_thread.join()

def add_notes_to_sing():
    start_time = time.time()
    for note in note_starts:
        while time.time() - start_time < note[1]:
            time.sleep(0.0001)
        song_notes_to_sing.append(note)
        print(f"START: {note}")

def remove_notes_to_sing():
    start_time = time.time()
    for note in note_ends:
        while time.time() - start_time < note[1]:
            time.sleep(0.0001)
        matching_note = next((n for n in song_notes_to_sing if n[0] == note[0]), None)
        if matching_note:
            song_notes_to_sing.remove(matching_note)
            #print(f"END: {note}")

def play_midi_file():
    pygame.midi.init()
    player = pygame.midi.Output(0)
    midi_file = mido.MidiFile(SONG_MIDI_PATH)
    current_time = 0

    for msg in midi_file:
        current_time += msg.time
        time.sleep(msg.time)

        if msg.type == 'note_on' and msg.velocity > 0:
            player.note_on(msg.note, msg.velocity)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            player.note_off(msg.note, 0)

    player.close()
    pygame.midi.quit()

if __name__ == "__main__":
    main()
