import pyaudio
import wave

# Parameters for recording
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1  # 1 channel
RATE = 44100  # 44.1kHz sampling rate
CHUNK = 1024  # 2^10 samples for buffer
RECORD_SECONDS = 6  # Time for recording
OUTPUT_FILENAME = "recorded_audio.wav"  # Name of the output file

# Initialize pyaudio
audio = pyaudio.PyAudio()

# Create the recording stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")

frames = []

# Record the audio
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Recording finished.")

# Stop and close the stream
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded data as a .wav file
wave_file = wave.open(OUTPUT_FILENAME, 'wb')
wave_file.setnchannels(CHANNELS)
wave_file.setsampwidth(audio.get_sample_size(FORMAT))
wave_file.setframerate(RATE)
wave_file.writeframes(b''.join(frames))
wave_file.close()

print(f"Audio saved as {OUTPUT_FILENAME}")
