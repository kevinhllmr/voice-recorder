import wave
import numpy as np
class echo:
    @staticmethod
    def add_echo(audio_path, output_path, delay_ms=500, decay=0.6):
        try:

            with wave.open(audio_path, 'rb') as wav_in:
                params = wav_in.getparams()
                framerate = wav_in.getframerate()
                n_channels = wav_in.getnchannels()
                sample_width = wav_in.getsampwidth()
                num_frames = wav_in.getnframes()

                audio_data = wav_in.readframes(params.nframes)
                samples = np.frombuffer(audio_data, dtype=np.int16)

            delay_samples = int(framerate * delay_ms / 1000)
            #result = np.zeros(len(samples) + delay_samples, dtype=np.int16)
            #result[:len(samples)] = samples

            result = samples.astype(np.float32)


            #for i in range(len(samples)):
            #   if i + delay_samples < len(result):
            #      result[i + delay_samples] += int(samples[i] * decay)
            for i in range(len(samples)):
                if i >= delay_samples:
                    result[i] += samples[i - delay_samples] * decay


            result = np.clip(result, -32768, 32767).astype(np.int16)

            with wave.open(output_path, 'wb') as wav_out:
                wav_out.setparams(params)
                wav_out.writeframes(result.tobytes())


            print(f"Echo-Effekt erfolgreich angewendet und gespeichert in '{output_path}'")
        except Exception as e:
            print(f"Fehler beim Anwenden des Echo-Effekts: {e}")