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

	def calculate_acoustic_index(folder, index_name, sample_rate=44100, fft_window_size=1024, hop_length=512, resolution_ms=60000, batch_size_in_file_count=1, num_bands=10): 
		on_file = 0
		audio_chunk = AudioSegment.empty()
		file_count = len(glob.glob(os.path.join(folder, "*")))
		index_values = []
		start = time.time()
		for file in sorted(glob.glob(os.path.join(folder, "*"))):
			on_file += 1
			audio_chunk += AudioSegment.from_file(file)
			if on_file % batch_size_in_file_count == 0 or on_file == file_count:
				print(f"batch {math.floor(on_file / batch_size_in_file_count)} out of {math.ceil(file_count / batch_size_in_file_count)}")
				audio_signal, sr = AudioChunkToLibrosa.audio_chunk_to_librosa(audio_chunk)
				chunks = AcousticTools.resolutionize(audio_signal, sr, resolution_ms)
				totallen = 0
				for chunk in chunks:
					if index_name == "ACI":
						index_values.append(AcousticTools.calculate_aci(sr, fft_window_size, hop_length, chunk))
					if index_name == "ADI":
						index_values.append(AcousticTools.calculate_adi(chunk, sr, num_bands))
				audio_chunk = AudioSegment.empty()
		end = time.time()
		print(index_values)
		print(f"that took {end - start} seconds.")	
		return index_values

	# Splits an audio file into the chunks. The acoustic index of each chunk will be calculated
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
	
	# Uses the mel spectogram and the number of bands to calculate AdI

	def calculate_adi(audio, sr, num_bands):
		mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=num_bands, power=1.0)
		band_amplitudes = np.sum(mel_spectrogram, axis=1)
		total_amplitude = np.sum(band_amplitudes)
		proportions = band_amplitudes / total_amplitude
		shannon_diversity_index = -np.sum(proportions * np.log(proportions + 1e-10))
		return shannon_diversity_index

	def resolutionize(audio, sr, resolution_ms):
		num_samples_per = int(sr * (resolution_ms / 1000.0))
		total_samples = len(audio)	
		duration_ms = int(librosa.get_duration(y=audio, sr=sr) * 1000)
		return [audio[start:start + resolution_ms] for start in range(0, total_samples, num_samples_per)]
