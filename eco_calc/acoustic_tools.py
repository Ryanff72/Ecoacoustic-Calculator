import ctypes
from tkinter import filedialog
import glob
import os
import librosa
import numpy as np
import tkinter as tk
from tkinter import messagebox
from scipy.signal import spectrogram
from scipy.signal import hilbert
from scipy.io import wavfile
from instance_manager import InstanceManager
from pydub import AudioSegment
import time
import math
from utils.audio_chunk_to_librosa import AudioChunkToLibrosa

class AcousticTools:

	
	# Calculates ACI based on parameters given.

	def calculate_acoustic_index(folder, index_name, fft_window_size=1024, hop_length=512, resolution_ms=60000, batch_size_in_file_count=1, num_bands=10): 
		errorbar = InstanceManager.get_instance("Errorbar")
		errorbar.errortxt.config(text=f"sup")
		print("resolution:")
		print(resolution_ms)
		on_file = 0
		audio_chunk = AudioSegment.empty()
		file_count = len(glob.glob(os.path.join(folder, "*")))
		index_values = []
		start = time.time()
		#errorbar.errortxt.config(text=f"Batch {math.ceil(on_file / batch_size_in_file_count)} out of {math.ceil(file_count / batch_size_in_file_count)}")
		for file in sorted(glob.glob(os.path.join(folder, "*"))):
			on_file += 1
			audio_chunk += AudioSegment.from_file(file)
			if on_file % batch_size_in_file_count == 0 or on_file == file_count:
				errorbar.update_text(text=f"Batch {math.ceil(on_file / batch_size_in_file_count)} out of {math.ceil(file_count / batch_size_in_file_count)}")
				print(f"Batch {math.ceil(on_file / batch_size_in_file_count)} out of {math.ceil(file_count / batch_size_in_file_count)}")
				audio_signal, sr = AudioChunkToLibrosa.audio_chunk_to_librosa(audio_chunk)
				chunks = AcousticTools.resolutionize(audio_signal, sr, resolution_ms)
				totallen = 0
				for chunk in chunks:
					if index_name == "ACI":
						index_values.append(AcousticTools.calculate_aci(sr, fft_window_size, hop_length, chunk))
					elif index_name == "ADI":
						index_values.append(AcousticTools.calculate_adi(chunk, sr, num_bands, fft_window_size, hop_length))
					elif index_name == "H":
						index_values.append(AcousticTools.calculate_shannon_diversity_index(chunk, sr, num_bands))
					elif index_name == "AEve":
						index_values.append(AcousticTools.calculate_aeve(chunk, sr, num_bands))
					elif index_name == "M":
						index_values.append(AcousticTools.calculate_m(chunk))
					elif index_name == "NDSI":
						index_values.append(AcousticTools.calculate_ndsi(chunk, sr, num_bands, fft_window_size, hop_length))
					elif index_name == "Bio":
						index_values.append(AcousticTools.calculate_bio(chunk, sr, num_bands, fft_window_size, hop_length))
				audio_chunk = AudioSegment.empty()
		end = time.time()
		print(index_values)
		print(f"that took {end - start} seconds.")	
		errorbar.update_text(text=f"That took {end-start} seconds.")
		return index_values
	


	# Splits an audio file into chunks. The acoustic index of each chunk will be calculated
	# seperately and be represented as a different data point.

	def calculate_aci(sr, fft_window_size, hop_length, audio):
		# f: Frequencies, t: Time bins, Sxx: Spectrogram (magnitude of frequency components over time)
		frequencies, time_bins, spectrogram_magnitude = spectrogram(
			audio,
			fs=sr,
			nperseg=fft_window_size,
			noverlap=fft_window_size - hop_length
		)

		# Calculate amplitude changes across time bins
		amplitude_changes = np.sum(np.abs(np.diff(spectrogram_magnitude, axis=1)), axis=1)

		# Calculate total amplitude for each frequency band
		total_band_amplitude = np.sum(spectrogram_magnitude, axis=1)

		# Normalize amplitude changes by total amplitude for each frequency band
		# Avoid division by zero using a small constant (1e-8)
		aci_per_frequency_band = amplitude_changes / (total_band_amplitude + 1e-8)

		# Compute the mean ACI across all frequency bands
		return np.mean(aci_per_frequency_band)
	
	# Uses the mel spectogram and the number of bands to calculate shannon diversity index

	def calculate_shannon_diversity_index(audio, sr, num_bands):
		mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=num_bands, power=1.0)
		band_amplitudes = np.sum(mel_spectrogram, axis=1)
		total_amplitude = np.sum(band_amplitudes)
		proportions = band_amplitudes / total_amplitude
		shannon_diversity_index = -np.sum(proportions * np.log(proportions + 1e-10))
		return shannon_diversity_index

	# calculates ADI

	def calculate_adi(audio, sr, num_bands, fft_window_size, hop_length):
		stft = np.abs(librosa.stft(audio, n_fft=fft_window_size, hop_length=hop_length))
		frequencies = librosa.fft_frequencies(sr=sr, n_fft=fft_window_size)
		band_edges = np.linspace(0, frequencies[-1], num_bands + 1)
		band_energies = []
		for i in range(len(band_edges) - 1):
			band_mask = (frequencies >= band_edges[i]) & (frequencies < band_edges[i+1])
			band_energy = np.sum(stft[band_mask, :] ** 2)
			band_energies.append(band_energy)
		band_energies = np.array(band_energies)
		total_energy = np.sum(band_energies)
		proportions = band_energies / (total_energy + 1e-10)
		shannon_i = -np.sum(proportions * np.log(proportions + 1e-10))
		adi = shannon_i / np.log(len(band_energies) + 1e-10)
		return max(adi, 0.0)

	# calculates Bioacoustic Index

	def calculate_bio(audio, sr, num_bands, fft_window_size, hop_length):
		stft = np.abs(librosa.stft(audio, n_fft=fft_window_size, hop_length=hop_length))
		frequencies = librosa.fft_frequencies(sr=sr, n_fft=fft_window_size)
		band_mask = (frequencies >= 2000) & (frequencies <= 11000)
		stft_band = stft[band_mask, :]
		energies = np.sum(stft_band ** 2, axis = 0)
		max_energy = np.max(energies)
		min_energy = np.min(energies)
		disparity = max_energy / (min_energy + 1e-10)
		return disparity

	# Calculates AEve

	def calculate_aeve(audio, sr, num_bands):
		shannon_diversity_index = AcousticTools.calculate_shannon_diversity_index(audio, sr, num_bands)
		aeve = 1 / (shannon_diversity_index + 1e-10)
		return aeve

	# Calculates median amplitude envelope

	def calculate_m(audio):
		signal = hilbert(audio)
		amplitude_envelope = np.abs(signal)
		m = np.median(amplitude_envelope)
		return m

	# Calculates median amplitude envelope

	def calculate_ndsi(audio, sr, num_bands, fft_window_size, hop_length):
		stft = np.abs(librosa.stft(audio, n_fft=fft_window_size, hop_length=hop_length))
		frequencies = librosa.fft_frequencies(sr=sr, n_fft=fft_window_size)
		anthrophony_band = (frequencies >= 1000) & (frequencies < 2000)
		biophony_band = (frequencies >= 2000) & (frequencies <= 11000)
		anthrophony_energy = np.sum(stft[anthrophony_band, :] ** 2)
		biophony_energy = np.sum(stft[biophony_band, :] ** 2)
		ndsi = (biophony_energy - anthrophony_energy) / (biophony_energy + anthrophony_energy + 1e-10) 
		return ndsi
	
	# This function splits the combined audio clip into clips of desired length

	def resolutionize(audio, sr, resolution_ms):
		num_samples_per = int(sr * (resolution_ms / 1000.0))
		total_samples = len(audio)	
		duration_ms = int(librosa.get_duration(y=audio, sr=sr) * 1000)
		return [audio[start:start + resolution_ms] for start in range(0, total_samples, num_samples_per)]
