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
		
		# store the data points so we can recreate the graph
		self.stored_indices = []
		self.stored_index_name = "ACI"
		self.previous_graph_widget = 0

		self.cur_graph_frame = tk.Frame(self)
		self.left_frame = tk.Frame(self)

		self.left_frame.grid(row=0, column=0, sticky="nsew")
		self.cur_graph_frame.grid(row=0, column=1, sticky="nsew")
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=2)
		

		# Left Column title
		left_col_title = tk.Label(self.left_frame, text="Graph Options", font=title_font)
		left_col_title.grid(row=0, column=0, padx=10, pady=(35, 5), sticky="nsew")

		# Graph Column title
		graph_col_title = tk.Label(self.cur_graph_frame, text="Graph", font=title_font)
		graph_col_title.grid(row=0, column=1, padx=10, pady=(35, 5), sticky="nsew")

		# Line type label
		left_col_title = tk.Label(self.left_frame, text="Line Type", font=label_font)
		left_col_title.grid(row=1, column=0, padx=10, pady=(35, 5), sticky="nsew")

        # Select Line Type Dropdown
		self.line_types = {"Solid Line" : "-", 
						   "Dashed Line" : "--", 
						   "Dash-dot Line" : "-.",
						   "Dotted Line" : ":"}
		self.line_type_dropdown = ttk.Combobox(self.left_frame, values=list(self.line_types.keys()), font=label_font)
		self.line_type_dropdown.grid(row=2, 
									 column=0, 
									 padx=10, 
									 pady=10)	
		self.line_type_dropdown.set("Solid Line")	
		self.line_type_dropdown.bind("<<ComboboxSelected>>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

		# Line thickness title
		left_col_title = tk.Label(self.left_frame, text="Line Thickness", font=label_font)
		left_col_title.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

		# Line thickness box
		self.line_thickness_box = tk.Entry(self.left_frame, width=10, font=label_font)
		self.line_thickness_box.grid(row=4, column = 0, padx=10, pady=0, sticky="ns")
		self.line_thickness_box.insert(0, "3")
		self.line_thickness_box.bind("<Return>", lambda event: self.create_graph(self.stored_index_name, self.stored_indices))

	def create_graph(self, index_name, indicies):
		self.stored_index_name = index_name
		self.stored_indices = indicies
		acoustic_index_figure = Figure(figsize=(5,4), dpi=120)
		plt=acoustic_index_figure.add_subplot(111)
		x_axis = list(range(1, len(indicies) + 1))
		plt.plot(x_axis, indicies, linestyle=self.line_types[self.line_type_dropdown.get()], linewidth=self.line_thickness_box.get(), marker='o')
		plt.set_title(index_name)
		plt.set_ylabel(index_name)
		plt.set_xlabel("Chunk Count")
		if (self.previous_graph_widget):
			self.previous_graph_widget.destroy()
		canvas = FigureCanvasTkAgg(acoustic_index_figure, master=self.cur_graph_frame)
		canvas_widget = canvas.get_tk_widget()
		canvas_widget.grid(row=1, column=1, padx=30, pady=30, sticky="nsew")
		self.previous_graph_widget = canvas_widget
		canvas.draw()

	def update_calculate_button(event, button, index):
		button.config(text=f"Calculate {index}")
