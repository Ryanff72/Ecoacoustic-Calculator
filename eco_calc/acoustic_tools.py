import ctypes
import socket
from tkinter import filedialog
import glob
import os
import json
import librosa
import numpy as np
import multiprocessing as mp
from multiprocessing import Pool, Manager
from numpy.fft import rfft, irfft
from maad import sound, features
import pyfftw.interfaces.numpy_fft as fft
import tkinter as tk
from tkinter import messagebox
from scipy import signal
from scipy.signal import spectrogram
from scipy.signal import hilbert
from scipy.io import wavfile
from instance_manager import InstanceManager
from pydub import AudioSegment
import time
import zlib
import math
from concurrent.futures import ThreadPoolExecutor
from utils.audio_chunk_to_librosa import AudioChunkToLibrosa

class AcousticTools:
	# some stored values to speed up calculations
	@classmethod
	def calculate_acoustic_index_server(self, folder, host, port, index_name, fft_window_size=1024, hop_length=512, resolution_ms=60000, batch_size_in_file_count=1, min_freq=20, max_freq=20000, bin_step=1000, min_bio=2000, max_bio=11000, min_anthro=1000, max_anthro=2000):
		errorbar = InstanceManager.get_instance("Errorbar")
		on_file = 0
		audio_chunk = AudioSegment.empty()
		file_count = len(glob.glob(os.path.join(folder, "*")))
		index_values = []
		start = time.time()

		port = int(port)

		files = sorted(glob.glob(os.path.join(folder, "*")))
		file_count = len(files)
		for i in range(0, file_count, batch_size_in_file_count):
		    batch_files = files[i:i + batch_size_in_file_count]
		    on_file = i + len(batch_files)
		    errorbar.update_text(text=f"Batch {math.ceil(on_file / batch_size_in_file_count)} out of {math.ceil(file_count / batch_size_in_file_count)}")

		    # Parallel file loading
		    def load_file(file):
		        return AudioSegment.from_file(file)
		    with ThreadPoolExecutor() as executor:
		        audio_chunks = list(executor.map(load_file, batch_files))
		    audio_chunk = sum(audio_chunks, AudioSegment.empty())

		    # Downsample and compress
		    audio_signal, sr = AudioChunkToLibrosa.audio_chunk_to_librosa(audio_chunk)
		    audio_signal = librosa.resample(audio_signal, orig_sr=sr, target_sr=16000)
		    sr = 16000

		    index_map = {"ACI": 0, "ADI": 1, "H": 2, "AEve": 3, "M": 4, "NDSI": 5, "Bio": 6}
		    params = np.array([
		        index_map.get(index_name, 0), fft_window_size, hop_length, resolution_ms,
		        min_freq, max_freq, bin_step, min_bio, max_bio, min_anthro, max_anthro
		    ], dtype=np.int32)
		    compressed_data = zlib.compress(audio_signal.tobytes())
		    data = (
		        sr.to_bytes(4, 'big') +
		        len(params.tobytes()).to_bytes(4, 'big') +
		        params.tobytes() +
		        compressed_data
		    )

		    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		        s.settimeout(30)
		        s.connect((host, port))
		        s.send(len(data).to_bytes(4, 'big') + data)

		        size_data = s.recv(4)
		        if not size_data:
		            print("No response size")
		            index_values.extend([0.0])
		            continue
		        data_size = int.from_bytes(size_data, 'big')

		        response_data = b""
		        while len(response_data) < data_size:
		            packet = s.recv(min(data_size - len(response_data), 65536))
		            if not packet:
		                print("Incomplete response")
		                break
		            response_data += packet

		        if response_data:
		            index_values.extend(np.frombuffer(response_data, dtype=np.float64))
		        else:
		            print("Empty response")
		            index_values.append(0.0)

		end = time.time()
		errorbar.update_text(text=f"That took {end - start} seconds for {file_count} files.")
		return index_values

	@classmethod
	def calculate_acoustic_index(self, folder, index_name, fft_window_size=1024, hop_length=512, resolution_ms=60000, batch_size_in_file_count=1, min_freq=20, max_freq=20000, bin_step=1000, min_bio=2000, max_bio=11000, min_anthro=1000, max_anthro = 2000): 
		errorbar = InstanceManager.get_instance("Errorbar")
		on_file = 0
		audio_chunk = AudioSegment.empty()
		file_count = len(glob.glob(os.path.join(folder, "*")))
		index_values = []
		start = time.time()

		for file in sorted(glob.glob(os.path.join(folder, "*"))):
			on_file += 1
			audio_chunk += AudioSegment.from_file(file)
			if on_file % batch_size_in_file_count == 0 or on_file == file_count:
				errorbar.update_text(text=f"Batch {math.ceil(on_file / batch_size_in_file_count)} out of {math.ceil(file_count / batch_size_in_file_count)}")
				audio_signal, sr = AudioChunkToLibrosa.audio_chunk_to_librosa(audio_chunk)
				chunks = AcousticTools.resolutionize(self, audio_signal, sr, resolution_ms, min_freq, max_freq)
				Sxx, tn, fn, _ = sound.spectrogram(audio_signal, sr, nperseg=fft_window_size, noverlap=fft_window_size - hop_length)

				def compute_index(chunk):
					if index_name == "ACI":
						_, _, aci = features.acoustic_complexity_index(Sxx)
						return aci
					elif index_name == "ADI":
						adi = features.acoustic_diversity_index(Sxx, fn, fmin=min_freq, fmax=max_freq, bin_step=bin_step)
						return adi[0] if isinstance(adi, tuple) else adi
					elif index_name == "H":
						h, _ = features.frequency_entropy(Sxx)
						return h
					elif index_name == "AEve":
						aeve = features.acoustic_eveness_index(Sxx, fn, fmin=min_freq, fmax=max_freq, bin_step=bin_step)
						return aeve[0] if isinstance(aeve, tuple) else aeve
					elif index_name == "M":
						return AcousticTools.calculate_m(chunk)
					elif index_name == "NDSI":
						ndsi, _, _ = features.soundscape_index(Sxx, fn, flim_bioPh=(min_bio, max_bio), flim_antroPh=(min_anthro, max_anthro))
						return ndsi
					elif index_name == "Bio":
						bio = features.bioacoustics_index(Sxx, fn, flim=[min_freq, max_freq])
						return bio
					return 0.0  # Default for invalid index_name

			from concurrent.futures import ThreadPoolExecutor
			with ThreadPoolExecutor(max_workers=min(len(chunks), os.cpu_count() or 4)) as executor:
				index_values.extend(executor.map(compute_index, chunks))

			audio_chunk = AudioSegment.empty()

		end = time.time()
		errorbar.update_text(text=f"That took {end - start} seconds.")
		print(index_values)
		return index_values
	
	# This function cuts off lowest and highest frequencies (some modification is required to restore this functionality)
	# TODO: optimize audio bandpass to make it so that it runs at an adequate speed.

	# This function splits the combined audio clip into clips of desired length. also applies bandpass

	def resolutionize(self, audio, sr, resolution_ms, min_freq, max_freq):
		#try:
			#self.mask
		#except AttributeError:
			#print("no mask!!!")
			#bins = len(audio) // 2 + 1
			#frequencies = np.linspace(0, sr / 2, bins, dtype=np.float32)
			#self.mask = ((frequencies >= min_freq) & (frequencies <= max_freq))
		audio_32 = audio.astype(np.float32, copy=False)
		#fft_data = fft.rfft(audio_32)
		#fft_data *= self.mask
		#bandpassed_audio = fft.irfft(fft_data, n=len(audio))
		processed_audio = audio_32
		num_samples_per = int(sr * (resolution_ms / 1000.0))
		total_samples = len(processed_audio)	
		duration_ms = int((total_samples / sr) * 1000)
		return [processed_audio[start:start + resolution_ms] for start in range(0, total_samples, num_samples_per)]

	# the code below has been removed in favor of scikit-maad.
	'''
	@classmethod
	def calculate_acoustic_index(self, folder, index_name, fft_window_size=1024, hop_length=512, resolution_ms=60000, batch_size_in_file_count=1, num_bands=10, min_freq=20, max_freq=20000, bin_step=1000, min_bio=2000, max_bio=11000, min_anthro=1000, max_anthro = 2000): 
		errorbar = InstanceManager.get_instance("Errorbar")
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
				#print(f"Batch {math.ceil(on_file / batch_size_in_file_count)} out of {math.ceil(file_count / batch_size_in_file_count)}")
			audio_signal, sr = AudioChunkToLibrosa.audio_chunk_to_librosa(audio_chunk)
			chunks = AcousticTools.resolutionize(self, audio_signal, sr, resolution_ms, min_freq, max_freq)
			Sxx, tn, fn, _ = sound.spectrogram(audio_signal, sr, nperseg=fft_window_size, noverlap=fft_window_size - hop_length)
			for chunk in chunks:
				if index_name == "ACI":
					_, _, aci = features.acoustic_complexity_index(Sxx)
					index_values.append(aci)
					#index_values.append(AcousticTools.calculate_aci(sr, fft_window_size, hop_length, chunk))
				elif index_name == "ADI":
					adi = features.acoustic_diversity_index(Sxx, fn, fmin=min_freq, fmax=max_freq, bin_step=bin_step)
					index_values.append(adi)
					#index_values.append(AcousticTools.calculate_adi(chunk, sr, num_bands, fft_window_size, hop_length))
				elif index_name == "H":
					h, _ = features.frequency_entropy(Sxx)
					index_values.append(h)
					#index_values.append(AcousticTools.calculate_shannon_diversity_index(chunk, sr, num_bands))
				elif index_name == "AEve":
					aeve = features.acoustic_eveness_index(Sxx, fn, fmin=min_freq, fmax=max_freq, bin_step=bin_step)
					index_values.append(aeve)
					#index_values.append(AcousticTools.calculate_aeve(chunk, sr, num_bands))
				elif index_name == "M":
					index_values.append(AcousticTools.calculate_m(chunk))
				elif index_name == "NDSI":
					ndsi, _, _ =features.soundscape_index(Sxx, fn, flim_bioPh=(min_bio, max_bio), flim_antroPh=(min_anthro, max_anthro))
					index_values.append(ndsi)
					#index_values.append(AcousticTools.calculate_ndsi(chunk, sr, num_bands, fft_window_size, hop_length))
				elif index_name == "Bio":
					bio = features.bioacoustics_index(Sxx, fn, flim=[min_freq, max_freq])
					index_values.append(bio)
					#index_values.append(AcousticTools.calculate_bio(chunk, sr, num_bands, fft_window_size, hop_length))
				audio_chunk = AudioSegment.empty()
		end = time.time()
		#del self.mask
		print(index_values)
		print(f"that took {end - start} seconds.")	
		errorbar.update_text(text=f"That took {end-start} seconds.")
		return index_values
	# seperately and be represented as a different data point.

	@classmethod
	def calculate_aci(self, sr, fft_window_size, hop_length, audio):
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

	@classmethod
	def calculate_shannon_diversity_index(self, audio, sr, num_bands):
		mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=num_bands, power=1.0)
		band_amplitudes = np.sum(mel_spectrogram, axis=1)
		total_amplitude = np.sum(band_amplitudes)
		proportions = band_amplitudes / total_amplitude
		shannon_diversity_index = -np.sum(proportions * np.log(proportions + 1e-10))
		return shannon_diversity_index

	# calculates ADI

	@classmethod
	def calculate_adi(self, audio, sr, num_bands, fft_window_size, hop_length):
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

	@classmethod
	def calculate_bio(self, audio, sr, num_bands, fft_window_size, hop_length):
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

	@classmethod
	def calculate_aeve(self, audio, sr, num_bands):
		shannon_diversity_index = AcousticTools.calculate_shannon_diversity_index(audio, sr, num_bands)
		aeve = 1 / (shannon_diversity_index + 1e-10)
		return aeve

	# Calculates median amplitude envelope
'''
	@classmethod
	def calculate_m(self, audio):
		signal = hilbert(audio)
		amplitude_envelope = np.abs(signal)
		m = np.median(amplitude_envelope)
		return m

'''
	# Calculates median amplitude envelope

	@classmethod
	def calculate_ndsi(self, audio, sr, num_bands, fft_window_size, hop_length):
		stft = np.abs(librosa.stft(audio, n_fft=fft_window_size, hop_length=hop_length))
		frequencies = librosa.fft_frequencies(sr=sr, n_fft=fft_window_size)
		anthrophony_band = (frequencies >= 1000) & (frequencies < 2000)
		biophony_band = (frequencies >= 2000) & (frequencies <= 11000)
		anthrophony_energy = np.sum(stft[anthrophony_band, :] ** 2)
		biophony_energy = np.sum(stft[biophony_band, :] ** 2)
		ndsi = (biophony_energy - anthrophony_energy) / (biophony_energy + anthrophony_energy + 1e-10) 
		return ndsi
'''	
