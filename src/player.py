import pyaudio
import wave

class Player:
    def __init__(self, on_playback_end_callback):
        self.playing = False
        self.paused = False
        self.playback_position = 0
        self.on_playback_end = on_playback_end_callback

    def play(self, update_waveform_callback):
        if not self.playing:
            self.playing = True
            if not self.paused:
                self.playback_position = 0
            self.paused = False
            chunk = 1024
            audio = pyaudio.PyAudio()
            with wave.open("recording.wav", 'rb') as wf:
                wf.setpos(self.playback_position)
                output_stream = audio.open(
                    format=audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                data = wf.readframes(chunk)
                while data and self.playing:
                    output_stream.write(data)
                    update_waveform_callback(data)
                    data = wf.readframes(chunk)
                    self.playback_position = wf.tell()

                output_stream.stop_stream()
                output_stream.close()
                
                if not data:
                    self.on_playback_end()

            audio.terminate()
            self.playing = False

    def pause(self):
        if self.playing:
            self.playing = False
            self.paused = True

    def stop(self):
        self.playing = False
        self.paused = False
        self.playback_position = 0
