import ctypes
import glob
import tkinter as tk
from tkinter import ttk
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class GraphPage(tk.Frame):
	def __init__(self, parent, controller, title_font, label_font, button_font):
		super().__init__(parent)

		self.cur_graph_frame = tk.Frame(self)
		self.cur_graph_frame.pack(fill=tk.BOTH, expand=True)

	def create_graph(self, index_name, indicies):
		acoustic_index_figure = Figure(figsize=(5,4), dpi=100)
		plt=acoustic_index_figure.add_subplot(111)
		x_axis = list(range(1, len(indicies) + 1))
		plt.plot(x_axis, indicies, linestyle='-', linewidth=2, marker='o')
		plt.set_title(index_name)
		plt.set_ylabel(index_name)
		plt.set_xlabel("Chunk Count")
		for widget in self.cur_graph_frame.winfo_children():
			widget.destroy()
		canvas = FigureCanvasTkAgg(acoustic_index_figure, master=self.cur_graph_frame)
		canvas_widget = canvas.get_tk_widget()
		canvas_widget.pack(fill=tk.BOTH, expand=True)
		canvas.draw()




	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")
