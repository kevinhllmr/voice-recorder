import pyaudio
import wave
import numpy as np
import os

class Player:
    def __init__(self, on_playback_end_callback):
        self.playing = False
        self.paused = False
        self.playback_position = 0
        self.on_playback_end = on_playback_end_callback
        self.volume = 1.0
        self.speed = 1.0

    def set_volume(self, volume):
        self.volume = max(0.0, min(2.0, volume))

    def set_speed(self, speed):
        self.speed = max(0.5, min(2.0, speed))

    def play(self, update_waveform_callback, file="recording.wav", raw_audio=None, params=None):
        if not self.playing:
            self.playing = True
            if not self.paused:
                self.playback_position = 0
            self.paused = False
            chunk = 1024
            audio = pyaudio.PyAudio()

            if raw_audio is not None and params is not None:
                self._play_raw_audio(raw_audio, params, update_waveform_callback, chunk, audio)
            else:
                if os.path.exists(file):
                    self._play_file_audio(file, update_waveform_callback, chunk, audio)
                else:
                    print("Error: Audio file not found.")
                    self.playing = False 

            self.playing = False

    def _play_raw_audio(self, raw_audio, params, update_waveform_callback, chunk, audio):
        output_stream = audio.open(
            format=audio.get_format_from_width(params.sampwidth),
            channels=params.nchannels,
            rate=int(params.framerate * self.speed),
            output=True
        )

        audio_data = np.frombuffer(raw_audio, dtype=np.int16)
        audio_data = np.int16(audio_data * self.volume)
        raw_audio = audio_data.tobytes()

        for i in range(0, len(raw_audio), chunk):
            if not self.playing:
                break
            frame = raw_audio[i:i + chunk]
            output_stream.write(frame)
            update_waveform_callback(frame)

        output_stream.stop_stream()
        output_stream.close()
        self.on_playback_end()

    def _play_file_audio(self, file, update_waveform_callback, chunk, audio):
        with wave.open(file, 'rb') as wf:
            wf.setpos(self.playback_position)
            output_stream = audio.open(
                format=audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=int(wf.getframerate() * self.speed),
                output=True
            )

            data = wf.readframes(chunk)
            while data and self.playing:
                audio_data = np.frombuffer(data, dtype=np.int16)
                audio_data = np.int16(audio_data * self.volume)
                data = audio_data.tobytes()
                output_stream.write(data)
                update_waveform_callback(data)
                data = wf.readframes(chunk)
                self.playback_position = wf.tell()

            output_stream.stop_stream()
            output_stream.close()

            if not data:
                self.on_playback_end()

    def pause(self):
        if self.playing:
            self.playing = False
            self.paused = True

    def stop(self):
        self.playing = False
        self.paused = False
        self.playback_position = 0
