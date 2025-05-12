import pyaudio
import numpy as np
from matplotlib import pyplot as plt

# Set up audio stream
# reduce chunk size and sampling rate for lower latency
CHUNK_SIZE = 1024  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Audio sampling rate (Hz)
VOLUME_THRESHOLD = 20
p = pyaudio.PyAudio()

# print info about audio devices
# let user select audio device
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

print('select audio device:')
input_device = int(input())

# open audio input stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                input_device_index=input_device)

'''# set up interactive plot
fig = plt.figure()
ax = plt.gca()
line, = ax.plot(np.zeros(CHUNK_SIZE))
ax.axhline(VOLUME_THRESHOLD, color='r', linestyle='--', label="Schwellwert")
ax.set_ylim(-30000, 30000)

plt.ion()
plt.show()'''

# Berechnung der lautesten (dominantesten) Frequenz
def get_dominant_frequency(data, rate):
    # Berechne die FFT des Audiosignals
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data), 1 / rate)

    # Nur positive Frequenzen berücksichtigen (erste Hälfte)
    positive_freqs = freqs[:len(freqs)//2]
    fft_magnitude = np.abs(fft_data[:len(fft_data)//2])

    # Finde die Frequenz mit der größten Amplitude
    dominant_freq = positive_freqs[np.argmax(fft_magnitude)]
    return dominant_freq

# Ausgabe der lautesten Frequenz aus aktuellem Audio-Stream
def get_audio_signal():
    # Read audio data from input stream
    data = stream.read(CHUNK_SIZE)

    # Convert audio data to numpy array
    audio_data = np.frombuffer(data, dtype=np.int16)

    '''# Update the plot
    line.set_ydata(audio_data)'''

    # Lautstärke des Signals (RMS-Wert)
    rms = np.sqrt(np.mean(np.square(audio_data)))

    # Wenn die Lautstärke über dem Schwellenwert liegt, berechne die Frequenz
    if rms > VOLUME_THRESHOLD:
        dominant_frequency = get_dominant_frequency(audio_data, RATE)
        #print(f"RMS: {rms:.2f}")
        # print(f"Dominante Frequenz: {dominant_frequency:.2f} Hz")
        return dominant_frequency
    else:
        # print("Kein Signal über dem Schwellwert")
        return 0
    
    '''# Redraw plot
    fig.canvas.draw()
    fig.canvas.flush_events()'''

def main():
    while True:
        get_audio_signal()

if __name__ == "__main__":
    main()