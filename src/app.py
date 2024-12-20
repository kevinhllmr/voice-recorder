import tkinter as tk
from threading import Thread
from recorder import Recorder
from player import Player
from waveform import Waveform
import os


class VoiceRecorderApp:
    def __init__(self, master):
        self.master = master
        self.recorder = Recorder()
        self.waveform = Waveform(self.master)
        self.audio_file = "recording.wav"

        self.recording_state = "IDLE"
        self.player = Player(self.on_playback_end)

        button_frame = tk.Frame(self.master)

        button_frame.pack(pady=10)

        self.record_toggle_button = tk.Button(button_frame, text="●", font=("FontAwesome", 24), command=self.toggle_recording, width=5, height=2, fg="red")
        self.record_toggle_button.pack(side='left', padx=5)

        self.play_pause_button = tk.Button(button_frame, text="▶", font=("FontAwesome", 24), command=self.toggle_play_pause, width=5, height=2, fg="green")
        self.play_pause_button.pack(side='left', padx=5)

        self.stop_button = tk.Button(button_frame, text="■", font=("FontAwesome", 24), command=self.stop_playback, width=5, height=2, fg="black")
        self.stop_button.pack(side='left', padx=5)

        self.update_buttons_state()

    def toggle_recording(self):
        if self.recording_state == "RECORDING":
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording_state = "RECORDING"
        self.update_buttons_state()

        def record():
            self.recorder.start_recording(self.waveform.update)

        Thread(target=record, daemon=True).start()

    def stop_recording(self):
        self.recorder.stop_recording()
        self.recording_state = "IDLE"
        self.recorder.save_recording()
        self.update_buttons_state()

    def toggle_play_pause(self):
        if self.player.playing:
            self.player.pause()
            self.recording_state = "PAUSED"
        else:
            if not os.path.exists(self.audio_file):
                return
            self.recording_state = "PLAYING"
            Thread(target=self.player.play, args=(self.update_waveform_in_main_thread,), daemon=True).start()
        self.update_buttons_state()

    def stop_playback(self):
        self.player.stop()
        self.recording_state = "IDLE"
        self.update_buttons_state()

    def update_waveform_in_main_thread(self, data):
        self.master.after(0, self.waveform.update, data)

    def on_playback_end(self):
        self.recording_state = "IDLE"
        self.update_buttons_state()

    def update_buttons_state(self):
        if self.recording_state == "IDLE":
            self.record_toggle_button.config(state='normal', text="●", font=("FontAwesome", 24), fg="red")
            self.play_pause_button.config(state='normal', text="▶", font=("FontAwesome", 24), fg="green")
            self.stop_button.config(state='disabled', text="■", font=("FontAwesome", 24), fg="black")
        elif self.recording_state == "RECORDING":
            self.record_toggle_button.config(state='normal', text="■", font=("FontAwesome", 24), fg="red")
            self.play_pause_button.config(state='disabled', text="▶", font=("FontAwesome", 24), fg="green")
            self.stop_button.config(state='disabled', text="■", font=("FontAwesome", 24), fg="black")
        elif self.recording_state == "PLAYING":
            self.record_toggle_button.config(state='disabled', text="●", font=("FontAwesome", 24), fg="red")
            self.play_pause_button.config(state='normal', text="⏸", font=("FontAwesome", 24), fg="black")
            self.stop_button.config(state='normal', text="■", font=("FontAwesome", 24), fg="black")
        elif self.recording_state == "PAUSED":
            self.record_toggle_button.config(state='disabled', text="●", font=("FontAwesome", 24), fg="red")
            self.play_pause_button.config(state='normal', text="▶", font=("FontAwesome", 24), fg="green")
            self.stop_button.config(state='normal', text="■", font=("FontAwesome", 24), fg="black")


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Crazy Voice Recorder")
    app = VoiceRecorderApp(root)
    root.mainloop()
