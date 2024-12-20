import pyaudio
import wave


class Recorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False

    def start_recording(self, waveform_callback=None):
        """
        Startet die Audioaufnahme und ruft den Callback für Wellenform-Updates auf.

        Args:
            waveform_callback (function): Funktion, die bei jedem aufgenommenen Chunk aufgerufen wird.
        """
        self.frames = []
        self.recording = True
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100

        try:
            self.stream = self.audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
            print("Aufnahme gestartet...")

            while self.recording:
                data = self.stream.read(chunk, exception_on_overflow=False)
                self.frames.append(data)

                # Aktualisiere die Wellenform, falls ein Callback übergeben wurde
                if waveform_callback:
                    waveform_callback(data)

        except Exception as e:
            print(f"Fehler während der Aufnahme: {e}")
        finally:
            print("Aufnahme beendet.")

    def stop_recording(self):
        """
        Stoppt die Audioaufnahme und schließt den Stream.
        """
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.stream = None

    def save_recording(self, filename="recording.wav"):
        """
        Speichert die aufgenommene Datei.

        Args:
            filename (str): Name der Datei, in die die Aufnahme gespeichert wird.
        """
        if not self.frames:
            print("Keine Aufnahme verfügbar, die gespeichert werden kann.")
            return

        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.frames))
            print(f"Aufnahme gespeichert: {filename}")
        except Exception as e:
            print(f"Fehler beim Speichern der Aufnahme: {e}")

    def close(self):
        """
        Schließt PyAudio und bereinigt Ressourcen.
        """
        self.audio.terminate()
        print("Recorder geschlossen.")