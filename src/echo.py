import wave
import numpy as np

class echo:
    @staticmethod
    def apply_echo(audio_path, delay_ms=500, decay=0.6):
        try:
            with wave.open(audio_path, 'rb') as wav_in:
                params = wav_in.getparams()
                framerate = wav_in.getframerate()
                num_frames = wav_in.getnframes()

                audio_data = wav_in.readframes(num_frames)
                samples = np.frombuffer(audio_data, dtype=np.int16)

            delay_samples = int(framerate * delay_ms / 1000)

            result = samples.astype(np.float32)

            for i in range(len(samples)):
                if i >= delay_samples:
                    result[i] += samples[i - delay_samples] * decay

            result = np.clip(result, -32768, 32767).astype(np.int16)

            return result.tobytes(), params
        except Exception as e:
            print(f"Fehler beim Anwenden des Echo-Effekts: {e}")
            return None, None