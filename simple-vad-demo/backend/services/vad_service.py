"""VAD service wrapper around the core VAD processor."""

import numpy as np
import asyncio
import logging

from services.vad_processor import SileroVADProcessor
from models.messages import VADResult

logger = logging.getLogger(__name__)


class VADService:
    """Service for voice activity detection."""
    
    # Silero VAD requires exactly 512 samples for 16kHz audio
    VAD_CHUNK_SIZE = 512
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 speech_threshold: float = 0.5,
                 silence_threshold: float = 0.3,
                 min_speech_duration_ms: int = 150,
                 min_silence_duration_ms: int = 400):
        """
        Initialize the VAD service.
        
        Args:
            sample_rate: Audio sample rate for VAD processing
            speech_threshold: Confidence threshold to start detecting speech
            silence_threshold: Confidence threshold to stop detecting speech
            min_speech_duration_ms: Minimum speech duration to trigger event
            min_silence_duration_ms: Minimum silence duration to trigger event
        """
        self.vad_processor = SileroVADProcessor(
            sample_rate=sample_rate,
            speech_threshold=speech_threshold,
            silence_threshold=silence_threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            min_silence_duration_ms=min_silence_duration_ms
        )
        # Buffer to accumulate audio samples until we have exactly 512 samples
        self.audio_buffer = np.array([], dtype=np.float32)
        
    async def process_audio(self, audio_chunk: np.ndarray) -> VADResult:
        """
        Process audio chunk with VAD.
        Buffers audio until we have exactly 512 samples, then processes.
        
        Args:
            audio_chunk: Audio data as numpy array
            
        Returns:
            VAD result with event and confidence (may be None/0.0 if buffering)
        """
        try:
            # Add incoming audio to buffer
            self.audio_buffer = np.concatenate([self.audio_buffer, audio_chunk])
            
            # Only process when we have enough samples
            if len(self.audio_buffer) >= self.VAD_CHUNK_SIZE:
                # Extract exactly VAD_CHUNK_SIZE samples
                vad_chunk = self.audio_buffer[:self.VAD_CHUNK_SIZE]
                # Keep the remainder in the buffer
                self.audio_buffer = self.audio_buffer[self.VAD_CHUNK_SIZE:]
                
                # Process with VAD (run in thread to avoid blocking)
                event, confidence = await asyncio.to_thread(
                    self.vad_processor.process_audio_chunk, 
                    vad_chunk
                )
                
                return VADResult(event=event, confidence=confidence)
            else:
                # Not enough samples yet, return no event
                logger.debug(f"Buffering audio: {len(self.audio_buffer)}/{self.VAD_CHUNK_SIZE} samples")
                return VADResult(event=None, confidence=0.0)
            
        except Exception as e:
            logger.error(f"VAD processing failed: {e}")
            return VADResult(event=None, confidence=0.0)
    
    def reset(self):
        """Reset VAD state and clear audio buffer."""
        self.vad_processor.reset_state()
        self.audio_buffer = np.array([], dtype=np.float32)
        
    @property
    def is_speaking(self) -> bool:
        """Check if currently detecting speech."""
        return self.vad_processor.is_speaking
