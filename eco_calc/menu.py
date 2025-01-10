import ctypes
import glob
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools
from toolbar import Toolbar
from settings_page import SettingsPage
from graph_page import GraphPage

class Menu(tk.Tk):

	def __init__(self):
		super().__init__()
		self.title("Ecoacoustic_Calculator")
		self.geometry("1000x600")

		# Font configuration
		self.title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
		self.label_font = tkFont.Font(family="Helvetica", size=14)
		self.button_font = tkFont.Font(family="Helvetica", size=14)

		self.toolbar = Toolbar(self, self.title_font, self.label_font, self.button_font)
		self.toolbar.pack(side="top", fill="x")

		self.container = tk.Frame(self)	
		self.container.pack(side="top", fill="both", expand=True)

		self.frames = {}

		for Page in (SettingsPage, GraphPage):
			page_name = Page.__name__
			frame = Page(parent=self.container, controller=self, title_font=self.title_font, label_font=self.label_font, button_font=self.button_font)
			self.frames[page_name] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.show_frame("SettingsPage")

	def show_frame(self, page_name):
		frame = self.frames[page_name]
		frame.tkraise()