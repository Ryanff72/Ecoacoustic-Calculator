from pydub import AudioSegment
import numpy as np
import librosa
import io

class AudioChunkToLibrosa:
    @staticmethod
    def audio_chunk_to_librosa(chunk):
        print(f"len: {len(chunk)}")
        samples = np.array(chunk.get_array_of_samples(), dtype=np.float32)
        
        # Handle stereo explicitly without reshaping issues
        if chunk.channels > 1:
            # Split channels and average manually to prevent reshaping errors
            left_channel = samples[0::2]
            right_channel = samples[1::2]
            samples = (left_channel + right_channel) / 2  # Combine to monoi
        
        # Normalize samples to [-1, 1] for consistent librosa processing
        samples /= 2**(8 * chunk.sample_width - 1)
        
        # Get the sampling rate
        sr = chunk.frame_rate
        
        return samples, sr