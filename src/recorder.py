import pyaudio
import wave
from tkinter import messagebox

class Recorder:
    def __init__(self):
        self.frames = []
        self.recording = False

    def start_recording(self, update_waveform_callback):
        self.recording = True
        self.frames = []
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100
        audio = pyaudio.PyAudio()
        input_stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        
        while self.recording:
            data = input_stream.read(chunk)
            self.frames.append(data)
            update_waveform_callback(data)
        
        input_stream.stop_stream()
        input_stream.close()
        audio.terminate()

    def stop_recording(self):
        self.recording = False

    def save_recording(self):
        if self.frames:
            with wave.open("recording.wav", 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.frames))
        else:
            messagebox.showwarning("Warning", "No recording to save.")
