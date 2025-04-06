import socket
import numpy as np
from maad import sound, features
from concurrent.futures import ThreadPoolExecutor
import os
import zlib
from utils.audio_chunk_to_librosa import AudioChunkToLibrosa
from acoustic_tools import AcousticTools

def compute_index(audio_signal, sr, index_name, fft_window_size, hop_length, resolution_ms, min_freq, max_freq, bin_step, min_bio, max_bio, min_anthro, max_anthro):
    """Compute the specified index for the given audio signal."""
    chunks = AcousticTools.resolutionize(None, audio_signal, sr, resolution_ms, min_freq, max_freq)
    Sxx, tn, fn, _ = sound.spectrogram(audio_signal, sr, nperseg=fft_window_size, noverlap=fft_window_size - hop_length)
    
    def calc_index(chunk):
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
        return 0.0

    with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
        index_values = list(executor.map(calc_index, chunks))
    print(index_values)
    return index_values

def start_server(host='0.0.0.0', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        
        size_data = client_socket.recv(4)
        if not size_data:
            client_socket.close()
            continue
        data_size = int.from_bytes(size_data, 'big')
        
        data = b""
        while len(data) < data_size:
            packet = client_socket.recv(min(data_size - len(data), 65536))
            if not packet:
                break
            data += packet
        
        sr = int.from_bytes(data[:4], 'big')
        param_size = int.from_bytes(data[4:8], 'big')
        params = np.frombuffer(data[8:8+param_size], dtype=np.int32)
        audio_signal = np.frombuffer(zlib.decompress(data[8+param_size:]), dtype=np.float64)
        
        index_name = ["ACI", "ADI", "H", "AEve", "M", "NDSI", "Bio"][params[0]]
        fft_window_size, hop_length, resolution_ms = params[1:4]
        min_freq, max_freq, bin_step = params[4:7]
        min_bio, max_bio, min_anthro, max_anthro = params[7:11]
        
        try:
            index_values = compute_index(
                audio_signal, sr, index_name, fft_window_size, hop_length, 
                resolution_ms, min_freq, max_freq, bin_step, min_bio, max_bio, 
                min_anthro, max_anthro
            )
        except Exception as e:
            print(f"Error: {e}")
            index_values = [0.0]
        
        result_data = np.array(index_values, dtype=np.float64).tobytes()
        client_socket.send(len(result_data).to_bytes(4, 'big') + result_data)
        client_socket.close()

if __name__ == "__main__":
    start_server()