import ctypes
import glob
import tkinter as tk
from tkinter import ttk
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools

class GraphPage(tk.Frame):
	def __init__(self, parent, controller, title_font, label_font, button_font):
		super().__init__(parent)

	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")
