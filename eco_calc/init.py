import ctypes
import platform
from menu import Menu

# Load acoustic calculator C library
eco_calc = ctypes.CDLL("./eco_calc.dll")

# Global Variables
target_audio_folder = ""

Menu.create_main_menu()