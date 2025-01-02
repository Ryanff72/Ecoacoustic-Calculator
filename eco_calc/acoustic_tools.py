import ctypes
from tkinter import filedialog
import glob
import os
import librosa
import numpy as np
from scipy.signal import spectrogram

class AcousticTools:
	def find_aci(folder, sample_rate=44100, fft_window_size=1024, hop_length=512): 
		print(f"folder: {folder}")
		print(f"User selected: {folder}")
		target_audio_files = glob.glob(f"{folder}/*")
		for file in target_audio_files:
			audio_signal, _ = librosa.load(file, sr=sample_rate)
			# Compute the spectrogram
			# f: Frequencies, t: Time bins, Sxx: Spectrogram (magnitude of frequency components over time)
			frequencies, time_bins, spectrogram_magnitude = spectrogram(
				audio_signal,
				fs=sample_rate,
				nperseg=fft_window_size,
				noverlap=fft_window_size - hop_length
			)
			# Calculate amplitude changes across time bins
			# Take the absolute difference between successive time bins for each frequency band
			amplitude_changes = np.sum(np.abs(np.diff(spectrogram_magnitude, axis=1)), axis=1)
			# Calculate total amplitude for each frequency band
			total_band_amplitude = np.sum(spectrogram_magnitude, axis=1)
			# Normalize amplitude changes by total amplitude for each frequency band
			# Avoid division by zero using a small constant (1e-8)
			aci_per_frequency_band = amplitude_changes / (total_band_amplitude + 1e-8)
			# Compute the mean ACI across all frequency bands
			aci = np.mean(aci_per_frequency_band)
			print(f"aci: {aci}")	
			return aci
