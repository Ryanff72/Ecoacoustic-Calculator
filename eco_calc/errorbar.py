import ctypes
import glob
import tkinter as tk
from tkinter import ttk
from tkinter import BOTH, LEFT, FLAT, SUNKEN, RAISED, GROOVE, RIDGE
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools

class Errorbar(tk.Frame):
	def __init__(self, parent, label_font):
		super().__init__(parent)

		self.errortxt = tk.Label(self, text="Welcome to the Ecoacoustic Calculator!", borderwidth=2, relief=GROOVE, font=label_font)
		self.errortxt.pack(side="left")

	def update_text(self, text):
		self.errortxt.config(text="")
		self.errortxt.config(text=text)
		self.errortxt.update_idletasks()