import tkinter as tk
from tkinter import ttk
from recorder import Recorder
from player import Player
from waveform import Waveform
import os
from threading import Thread
from echo import echo 

class VoiceRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master = master
        main_frame= tk.Frame(self.master)
        main_frame.pack(padx=20, pady=20)
        
        tk.Label(main_frame, text="Crazy Voice Recorder", font=("FontAwesome", 24)).grid(row=0, column=0, columnspan=2, pady=10)

        
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

        slider_frame = tk.Frame(self.master)
        slider_frame.pack(pady=10)

        tk.Label(slider_frame, text="Lautstärke").pack(side='left', padx=5)
        self.volume_slider = ttk.Scale(slider_frame, from_=0, to_=2, orient='horizontal', command=self.update_volume)
        self.volume_slider.set(1.0)
        self.volume_slider.pack(side='left', padx=5)

        tk.Label(slider_frame, text="Geschwindigkeit").pack(side='left', padx=5)
        self.speed_slider = ttk.Scale(slider_frame, from_=0.5, to_=2, orient='horizontal', command=self.update_speed)
        self.speed_slider.set(1.0) 
        self.speed_slider.pack(side='left', padx=5)
        
        #self.echo_button = tk.Button(button_frame, text="Echo", font=("Arial", 12), command=self.add_echo_effect, width=10)
        #self.echo_button.pack(side='left', padx=5)

        self.echo_var = tk.BooleanVar()  
        self.echo_checkbutton = tk.Checkbutton(self.master, text="Echo-Effekt", variable=self.echo_var, command=self.update_echo_effect)
        self.echo_checkbutton.pack(pady=5)
        
        tk.Label(self.master, text="Verzögerung (ms)").pack(pady=5)
        self.delay_slider = ttk.Scale(self.master, from_=100, to_=2000, orient='horizontal')
        self.delay_slider.set(500)
        self.delay_slider.pack(pady=5)

        tk.Label(self.master, text="Abklingen").pack(pady=5)
        self.decay_slider = ttk.Scale(self.master, from_=0.1, to_=1.0, orient='horizontal')
        self.decay_slider.set(0.6)
        self.decay_slider.pack(pady=5)


        self.update_buttons_state()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
                   
    def toggle_recording(self):
        if self.recording_state == "RECORDING":
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording_state = "RECORDING"
        self.update_buttons_state()

        def record():
            self.recorder.start_recording(self.update_waveform_in_main_thread)

        self.recording_thread = Thread(target=record, daemon=True)
        self.recording_thread.start()

    def stop_recording(self):
        self.recorder.stop_recording()
        self.recording_state = "IDLE"
        self.recorder.save_recording(self.audio_file)
        self.update_buttons_state()

    def toggle_play_pause(self):
        if self.player.playing:
            self.player.pause()
            self.recording_state = "PAUSED"
        else:
            if not os.path.exists(self.audio_file):
                return
            self.recording_state = "PLAYING"

            def play():
                if self.echo_var.get():  
                    self.player.play(update_waveform_callback=self.update_waveform_in_main_thread, file=self.effect_file)
                else:
                    self.player.play(update_waveform_callback=self.update_waveform_in_main_thread, file=self.audio_file)

            self.playback_thread = Thread(target=play, daemon=True)
            self.playback_thread.start()

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
    
    def add_echo_effect(self):
        if not os.path.exists(self.audio_file):
            print("Keine Aufnahme gefunden!")
            return
        self.effect_file = "recording_with_echo.wav"
        delay = int(self.delay_slider.get())
        decay = float(self.decay_slider.get())
        try:
            echo.add_echo(self.audio_file, self.effect_file, delay_ms=delay, decay=decay)
            print(f"Echo-Effekt angewendet und gespeichert in {self.effect_file}")
        except Exception as e:
            print(f"Fehler beim Anwenden des Echo-Effekts: {e}")
            
            
    def update_echo_effect(self):
        """Aktualisiert den Effekt, je nachdem, ob der Haken gesetzt ist oder nicht"""
        if self.echo_var.get():  #
            print("Echo-Effekt wird angewendet.")
            self.add_echo_effect()
        else:
            print("Echo-Effekt deaktiviert.")


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

    def update_volume(self, value):
        self.player.set_volume(float(value))

    def update_speed(self, value):
        self.player.set_speed(float(value))

    def on_closing(self):
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Voice Recorder")
    app = VoiceRecorderApp(root)
    root.mainloop()
