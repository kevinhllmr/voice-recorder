import librosa
import numpy as np
import scipy.signal as sig
import soundfile as sf
from librosa.core import note_to_hz
import psola 

SEMITONES_IN_OCTAVE = 12

def get_closest_pitch(value, scale):
    if np.isnan(value):
        return np.nan
    
    degrees = librosa.key_to_degrees(scale)
    degrees = np.concatenate((degrees, [degrees[0] + SEMITONES_IN_OCTAVE]))

    midi_note = librosa.hz_to_midi(value)
    degree = librosa.hz_to_midi(value) % SEMITONES_IN_OCTAVE
    closest_pitch_class = np.argmin(np.abs(degrees - degree))

    degree_diff = degree - degrees[closest_pitch_class]
    midi_note -= degree_diff
    return librosa.midi_to_hz(midi_note)

def calculate_correct_pitch(f0, scale):
    closest = np.zeros_like(f0)
    for i in range(f0.shape[0]): 
        closest[i] = get_closest_pitch(f0[i], scale)

    med_filtered = sig.medfilt(closest, kernel_size=11)
    med_filtered[np.isnan(med_filtered)] = closest[np.isnan(med_filtered)]
    return med_filtered

def autotune(y, sr, scale):
    fmin = librosa.note_to_hz('C2')
    fmax = librosa.note_to_hz('C7')
    frame_length = 2048
    hop_length = frame_length // 4
    
    f0, voiced_flag, voiced_prob = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=sr, 
                                                frame_length=frame_length, hop_length=hop_length)
    
    corrected_f0 = calculate_correct_pitch(f0, scale)

    pitch_shifted = psola.vocode(y, sample_rate=int(sr), 
                                 target_pitch=corrected_f0, fmin=fmin, fmax=fmax)
    return pitch_shifted

def main():
    audio_file_path = 'recording.wav'

    y, sr = librosa.load(audio_file_path, mono=True)
    print(f"Audio time series: {y}")
    print(f"Sampling rate: {2*sr} Hz")

    scale = "C:min"
    autotune_result = autotune(y, 2*sr, scale)
    
    filepath = "autotune.wav"
    sf.write(filepath, autotune_result, sr)

if __name__ == "__main__":
    main()