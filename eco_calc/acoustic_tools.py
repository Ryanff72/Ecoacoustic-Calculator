import ctypes
from tkinter import filedialog
import glob
import os
import librosa
import numpy as np
from scipy.signal import spectrogram
from pydub import AudioSegment
import time
import math
from utils.audio_chunk_to_librosa import AudioChunkToLibrosa

class AcousticTools:

	# Calculates ACI based on parameters given.

	def find_aci(folder, sample_rate=44100, fft_window_size=1024, hop_length=512, resolution_ms=60000): 
		start = time.time()
		audio_signal, sr = AcousticTools.combine_audio(folder)
		chunks = AcousticTools.resolutionize(audio_signal, sr, resolution_ms)
		totallen = 0
		for chunk in chunks:
			totallen += len(chunk)	
			# Compute the spectrogram
			# f: Frequencies, t: Time bins, Sxx: Spectrogram (magnitude of frequency components over time)
			frequencies, time_bins, spectrogram_magnitude = spectrogram(
				chunk,
				fs=sr,
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
		print(f"there were {len(chunks)} chunks")
		print(f"total len: {totallen}")
		end = time.time()
		print(f"letime: {end - start}")	
		return aci

	# Combines every audio (.wav) file in a folder. Returns the resulting audio signal.

	def combine_audio(folder):
		print(f"Combining audio files in folder: {folder}")
		audio_chunk = AudioSegment.empty()
		for file in sorted(glob.glob(os.path.join(folder, "*"))):
			audio_chunk += AudioSegment.from_file(file)
		return AudioChunkToLibrosa.audio_chunk_to_librosa(audio_chunk)

	# Splits an audio file into the chunks. The acoustic index of each chunk will be calculated
	# seperately and be represented as a different data point.

	def resolutionize(audio, sr, resolution_ms):
		num_samples_per = int(sr * (resolution_ms / 1000.0))
		total_samples = len(audio)	
		duration_ms = int(librosa.get_duration(y=audio, sr=sr) * 1000)
		return [audio[start:start + resolution_ms] for start in range(0, total_samples, num_samples_per)]