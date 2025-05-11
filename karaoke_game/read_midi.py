import mido
from mido import MidiFile

def midi_to_timecoded_frequencies(midi_file_path):
    midi_file = mido.MidiFile(midi_file_path)
    frequencies_timecoded = [] # Liste der Noten bestehend aus Frequenz, Start- und Endzeitpunkt
    notes_started = {} # Temporäre Liste gestarteter Noten, deren Ende noch nicht bekannt ist
    current_time = 0

    for msg in midi_file:
        current_time += msg.time
        # Note aktiviert
        if msg.type == "note_on" and msg.velocity > 0:
            notes_started[msg.note] = current_time # Speichert aktivierten Midi-Wert zusammen mit Startzeit
        # Note deaktiviert
        elif (msg.type == "note_off") or (msg.type == 'note_on' and msg.velocity == 0):
            start_time = notes_started[msg.note] # Startzeitpunkt zu deaktivierter Note holen und...
            del notes_started[msg.note] # ...temporären Eintrag aus notes_started löschen
            if start_time is not None:
                frequency = midi_note_to_frequency(msg.note) # Midi-Note in Hz
                frequencies_timecoded.append((start_time, current_time, frequency)) # Note mit Startzeit, Endzeit und Frequenz abspeichern

    frequencies_timecoded.sort(key=lambda n: n[0])  # Nach Startzeit sortieren (in die richtige Reihenfolge bringen)
    return frequencies_timecoded


def midi_note_to_frequency(note):
    return 440.0 * 2 ** ((note - 69) / 12)