import ctypes
import tkinter as tk
import platform
from tkinter import filedialog

# Load acoustic calculator C library
eco_calc = ctypes.CDLL("./eco_calc.dll")

print(platform.architecture())

def open_folder():
    file_path = filedialog.askdirectory(title="Select a File")
    if file_path:
        print(f"User selected: {file_path}")
        eco_calc.x()

# Create a Window
root = tk.Tk()
root.title("Ecoacoustic_Calculator")
root.geometry("640x480")

# File Import Button
file_import_button = tk.Button(root, text="File", command=open_folder)
file_import_button.pack(pady=50)
file_import_button.place(x=5,y=5)

# Event Loop
root.mainloop()