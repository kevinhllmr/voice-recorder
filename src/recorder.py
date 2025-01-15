import pyaudio
import wave
import numpy as np

class Recorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.live_playback = False
        self.live_stream = None

    def enable_live_playback(self):
        self.live_playback = True
        if not self.live_stream:
            self.live_stream = self.audio.open(
                format=pyaudio.paInt16, 
                channels=1, 
                rate=44100, 
                output=True, 
                frames_per_buffer=1024
            )

    def disable_live_playback(self):
        self.live_playback = False
        if self.live_stream:
            self.live_stream.stop_stream()
            self.live_stream.close()
            self.live_stream = None

    def start_recording(self, waveform_callback=None):
        self.frames = []
        self.recording = True
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100

        try:
            self.stream = self.audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
            while self.recording:
                data = self.stream.read(chunk, exception_on_overflow=False)
                self.frames.append(data)

                if waveform_callback:
                    waveform_callback(data)

                if self.live_playback and self.live_stream:
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    self.live_stream.write(audio_data.tobytes())

        except Exception as e:
            print(f"Error during recording: {e}")
        finally:
            print("Recording stopped.")

    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.stream = None

    def save_recording(self, filename="recording.wav"):
        if not self.frames:
            print("No recording to save.")
            return
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.frames))
            print(f"Recording saved to {filename}")
        except Exception as e:
            print(f"Error saving recording: {e}")

    def close(self):
        if self.live_stream:
            self.live_stream.stop_stream()
            self.live_stream.close()
        self.audio.terminate()
        print("Recorder closed.")
