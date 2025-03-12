import ctypes
import glob
import tkinter as tk
import numpy as np
from tkinter import ttk
from tkinter import GROOVE
import platform
from directory_operations import DirectoryOperations
from acoustic_tools import AcousticTools
from scipy.interpolate import make_interp_spline
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class GraphPage(tk.Frame):
	def __init__(self, parent, controller, title_font, label_font, button_font):
		super().__init__(parent)
		
		# store the data points so we can recreate the graph
		self.stored_indices = []
		self.stored_index_name = ""
		self.previous_graph_widget = 0

		self.cur_graph_frame = tk.Frame(self, borderwidth=2, relief=GROOVE)
		self.left_frame = tk.Frame(self, borderwidth=2, relief=GROOVE)

		self.left_frame.grid(row=0, column=0, sticky="nsew")
		self.cur_graph_frame.grid(row=0, column=1, sticky="ew")
		
		# Make it fill the screen
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=2)

		# Left Column title
		left_col_title = tk.Label(self.left_frame, text="Graph Options", font=title_font)
		left_col_title.grid(row=0, column=0, padx=10, pady=(35, 5), sticky="nsew")

		# Graph Column title
		graph_col_title = tk.Label(self.cur_graph_frame, text="Graph", font=title_font)
		graph_col_title.grid(row=0, column=1, padx=(60,0), pady=(35, 5), sticky="nsew")

		# Line type label
		left_col_title = tk.Label(self.left_frame, text="Line Type", font=label_font)
		left_col_title.grid(row=1, column=0, padx=10, pady=2, sticky="nsew")

        # Select Line Type Dropdown
		self.line_types = {
						   "Solid Line" : "-", 
						   "Dashed Line" : "--", 
						   "Dash-dot Line" : "-.",
						   "Dotted Line" : ":"
						   }
		self.line_type_dropdown = ttk.Combobox(self.left_frame, values=list(self.line_types.keys()), font=label_font)
		self.line_type_dropdown.grid(row=2, 
									 column=0, 
									 padx=10, 
									 pady=2)	
		self.line_type_dropdown.set("Solid Line")	
		self.line_type_dropdown.bind("<<ComboboxSelected>>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		# Line thickness title
		left_col_title = tk.Label(self.left_frame, text="Line Thickness", font=label_font)
		left_col_title.grid(row=3, column=0, padx=10, pady=2, sticky="nsew")

		# Line thickness box
		self.line_thickness_box = tk.Entry(self.left_frame, width=10, font=label_font)
		self.line_thickness_box.grid(row=4, column = 0, padx=10, pady=2, sticky="ns")
		self.line_thickness_box.insert(0, "3")
		self.line_thickness_box.bind("<Return>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		# Line type label
		line_type_title = tk.Label(self.left_frame, text="Line Smoothness", font=label_font)
		line_type_title.grid(row=5, column=0, padx=10, pady=2, sticky="nsew")

        # Select Line Type Dropdown
		self.line_smoothnesses = {
							"No Smoothing" : 0, 
						    "Moderate Smoothing" : 30, 
						   	"High Smoothing" : 500
						}
		self.line_smoothness_dropdown = ttk.Combobox(self.left_frame, values=list(self.line_smoothnesses.keys()), font=label_font)
		self.line_smoothness_dropdown.grid(row=6, 
									 column=0, 
									 padx=10, 
									 pady=2)	
		self.line_smoothness_dropdown.set("No Smoothing")	
		self.line_smoothness_dropdown.bind("<<ComboboxSelected>>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		# Marker size label
		self.marker_size_label = tk.Label(self.left_frame, text="Marker Size", font=label_font)
		self.marker_size_label.grid(row=7, column=0, padx=10, pady=2, sticky="nsew")

		# Marker size box
		self.marker_size_box = tk.Entry(self.left_frame, width=10, font=label_font)
		self.marker_size_box.grid(row=8, column = 0, padx=10, pady=2, sticky="ns")
		self.marker_size_box.insert(0, "0")
		self.marker_size_box.bind("<Return>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		# Marker size label
		self.marker_type_label = tk.Label(self.left_frame, text="Marker Type", font=label_font)
		self.marker_type_label.grid(row=9, column=0, padx=10, pady=2, sticky="nsew")

		# Select marker type dropdown 
		self.line_marker_types = {
							"Point" : ".", 
						    "Circle" : "o", 
						   	"Square" : "s",
						   	"Triangle Up" : "^",
						   	"Triangle Down" : "v",
						   	"Star" : "*",
						   	"Plus" : "+",
						   	"X" : "x",
						}
		self.line_marker_types_dropdown = ttk.Combobox(self.left_frame, values=list(self.line_marker_types.keys()), font=label_font)
		self.line_marker_types_dropdown.grid(row=10, 
									 column=0, 
									 padx=10, 
									 pady=2)	
		self.line_marker_types_dropdown.set("Point")	
		self.line_marker_types_dropdown.bind("<<ComboboxSelected>>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))
		
		# Line color title
		line_color_title = tk.Label(self.left_frame, text="R,G,B Colors (0-255)", font=label_font)
		line_color_title.grid(row=11, column=0, padx=10, pady=2, sticky="nsew")

		# Line color box
		self.line_red_color_box = tk.Entry(self.left_frame, width=10, font=label_font)
		self.line_red_color_box.grid(row=12, column = 0, padx=10, pady=2, sticky="ns")
		self.line_red_color_box.insert(0, "50")
		self.line_red_color_box.bind("<Return>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		self.line_green_color_box = tk.Entry(self.left_frame, width=10, font=label_font)
		self.line_green_color_box.grid(row=13, column = 0, padx=10, pady=2, sticky="ns")
		self.line_green_color_box.insert(0, "100")
		self.line_green_color_box.bind("<Return>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		self.line_blue_color_box = tk.Entry(self.left_frame, width=10, font=label_font)
		self.line_blue_color_box.grid(row=14, column = 0, padx=10, pady=2, sticky="ns")
		self.line_blue_color_box.insert(0, "150")
		self.line_blue_color_box.bind("<Return>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		self.create_graph(self.stored_index_name, self.stored_indices)

	def create_graph(self, index_name, indicies):
		self.stored_index_name = index_name
		self.stored_indices = indicies
		acoustic_index_figure = Figure(figsize=(6,4.5), dpi=120)
		plt=acoustic_index_figure.add_subplot(111)
		x_axis = list(range(1, len(indicies) + 1))
		# make graph smooth
		if (self.line_smoothnesses[self.line_smoothness_dropdown.get()] != 0):
			x = np.array(x_axis)
			y = np.array(indicies)
			X_Y_Spline = make_interp_spline(x, y)
			x = np.linspace(x.min(), x.max(), self.line_smoothnesses[self.line_smoothness_dropdown.get()])
			y = X_Y_Spline(x)
			indicies = y
			x_axis = x
		# plot data
		plt.plot(
			x_axis, 
			indicies, 
			linestyle=self.line_types[self.line_type_dropdown.get()], 
			linewidth=self.line_thickness_box.get(), 
			markersize=self.marker_size_box.get(),
			marker=self.line_marker_types[self.line_marker_types_dropdown.get()],
			color=
				(float(self.line_red_color_box.get()) / 255,
				float(self.line_green_color_box.get()) / 255,
				float(self.line_blue_color_box.get()) / 255)
			)
		plt.set_yscale('linear')
		plt.yaxis.get_major_formatter().set_useOffset(False)
		plt.yaxis.get_major_formatter().set_scientific(False)
		plt.set_title(index_name)
		plt.set_ylabel(index_name)
		plt.set_xlabel("Chunk Count")
		if (self.previous_graph_widget):
			self.previous_graph_widget.destroy()
		canvas = FigureCanvasTkAgg(acoustic_index_figure, master=self.cur_graph_frame)
		canvas_widget = canvas.get_tk_widget()
		canvas_widget.grid(row=1, column=1, padx=(50,0), pady=0, sticky="nesw")
		self.previous_graph_widget = canvas_widget
		canvas.draw()

	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")
