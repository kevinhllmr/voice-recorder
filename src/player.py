import pyaudio
import wave
import numpy as np

class Player:
    def __init__(self, on_playback_end_callback):
        self.playing = False
        self.paused = False
        self.playback_position = 0
        self.on_playback_end = on_playback_end_callback
        self.volume = 1.0  # Lautstärke (1.0 = Originallautstärke)
        self.speed = 1.0   # Geschwindigkeit (1.0 = normale Geschwindigkeit)
        self.audio_stream = None

    def set_volume(self, volume):
        self.volume = volume

    def set_speed(self, speed):
        self.speed = speed

    def play(self, update_waveform_callback):
        if not self.playing:
            self.playing = True
            chunk = 1024
            audio = pyaudio.PyAudio()

            with wave.open("recording.wav", 'rb') as wf:
                output_stream = audio.open(
                    format=audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=int(wf.getframerate() * self.speed),  # Geschwindigkeit anpassen
                    output=True
                )

                data = wf.readframes(chunk)
                while data and self.playing:
                    # Lautstärke anpassen
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    audio_data = np.int16(audio_data * self.volume)
                    data = audio_data.tobytes()

                    output_stream.write(data)
                    update_waveform_callback(data)
                    data = wf.readframes(chunk)
                    self.playback_position = wf.tell()

                output_stream.stop_stream()
                output_stream.close()

            audio.terminate()
            self.playing = False
            self.on_playback_end()