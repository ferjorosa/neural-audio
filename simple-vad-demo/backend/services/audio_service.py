"""Audio processing service for decoding and resampling."""

import numpy as np
import sphn
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AudioService:
    """Handles audio decoding and resampling operations."""
    
    def __init__(self, sample_rate: int = 24000):
        """
        Initialize the audio service.
        
        Args:
            sample_rate: Input sample rate from Opus decoder
        """
        self.sample_rate = sample_rate
        # OpusStreamReader handles Ogg container format automatically
        self.opus_reader = sphn.OpusStreamReader(sample_rate)
        self.audio_buffer = np.array([], dtype=np.float32)
        
    def decode_opus(self, opus_data: bytes) -> Optional[np.ndarray]:
        """
        Decode Opus audio data (in Ogg container format) to PCM.
        
        Args:
            opus_data: Ogg-encapsulated Opus audio data
            
        Returns:
            Decoded audio as numpy array (float32), or None if decoding fails
        """
        try:
            # OpusStreamReader.append_bytes() handles Ogg pages and returns decoded PCM
            # It returns a numpy array of float32 samples
            audio_array = self.opus_reader.append_bytes(opus_data)
            
            # Log audio level for debugging (only when meaningful)
            if len(audio_array) > 0:
                rms = np.sqrt(np.mean(audio_array ** 2))
                logger.debug(f"🎵 Backend: Decoded audio: {len(audio_array)} samples, RMS level: {rms:.4f}")
            
            return audio_array if len(audio_array) > 0 else None
            
        except Exception as e:
            logger.error(f"Failed to decode Opus data: {e}")
            return None
    
    def resample_24k_to_16k(self, audio_24k: np.ndarray) -> np.ndarray:
        """
        Resample audio from 24kHz to 16kHz using simple decimation.
        
        Args:
            audio_24k: Audio data at 24kHz
            
        Returns:
            Resampled audio at 16kHz
        """
        # Add to buffer
        self.audio_buffer = np.concatenate([self.audio_buffer, audio_24k])
        
        # Decimate by factor of 1.5 (24000/16000)
        if len(self.audio_buffer) >= 3:
            # Simple decimation - take every 1.5th sample
            indices = np.arange(0, len(self.audio_buffer), 1.5).astype(int)
            resampled = self.audio_buffer[indices]
            
            # Keep remainder for next chunk
            last_used_idx = indices[-1] if len(indices) > 0 else 0
            self.audio_buffer = self.audio_buffer[last_used_idx:]
            
            return resampled
        
        return np.array([], dtype=np.float32)
    
    def process_opus_chunk(self, opus_data: bytes) -> Optional[np.ndarray]:
        """
        Complete pipeline: decode Opus (from Ogg pages) and resample to 16kHz.
        
        Args:
            opus_data: Ogg-encapsulated Opus audio data
            
        Returns:
            Resampled audio at 16kHz, or None if processing fails
        """
        # Decode Opus to 24kHz PCM
        audio_24k = self.decode_opus(opus_data)
        if audio_24k is None:
            return None
            
        # Resample to 16kHz for VAD
        audio_16k = self.resample_24k_to_16k(audio_24k)
        
        return audio_16k if len(audio_16k) > 0 else None
    
    def reset(self):
        """Reset the audio buffer state."""
        self.audio_buffer = np.array([], dtype=np.float32)
