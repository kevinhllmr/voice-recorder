import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Waveform:
    def __init__(self, master):
        self.figure, self.ax = plt.subplots(figsize=(8, 2))
        self.ax.set_ylim(-32768, 32767)
        self.line, = self.ax.plot([], [], lw=1)
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update(self, data):
        audio_data = np.frombuffer(data, dtype=np.int16)
        self.line.set_ydata(audio_data)
        self.line.set_xdata(range(len(audio_data)))
        self.ax.set_xlim(0, len(audio_data))
        self.canvas.draw()