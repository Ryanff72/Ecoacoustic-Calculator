import ctypes
import glob
import tkinter as tk
from tkinter import ttk
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools

class Toolbar(tk.Frame):
	def __init__(self, parent, title_font, label_font, button_font):
		super().__init__(parent)

		# File Import Button
		file_import_button = tk.Button(self, text="File", command=DirectoryOperations.open_folder, font=button_font)
		file_import_button.pack(side="left")

		# Settings Page Button
		settings_page_button = tk.Button(self, text="Settings", command=lambda: parent.show_frame("SettingsPage"), font=button_font).pack(side="left")

		# Graph Page Button
		graph_page_button = tk.Button(self, text="Graphs", command=lambda: parent.show_frame("GraphPage"), font=button_font).pack(side="left")
