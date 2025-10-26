import torch
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SileroVADProcessor:
    """
    Silero VAD processor for real-time voice activity detection.
    
    This class handles:
    - Loading the Silero VAD model
    - Processing audio chunks to detect speech
    - Maintaining state for hysteresis (avoiding flickering)
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 speech_threshold: float = 0.5,
                 silence_threshold: float = 0.3,
                 min_speech_duration_ms: int = 100,
                 min_silence_duration_ms: int = 300):
        """
        Initialize the VAD processor.
        
        Args:
            sample_rate: Audio sample rate (Silero VAD works best with 16kHz)
            speech_threshold: Probability threshold to start detecting speech
            silence_threshold: Probability threshold to stop detecting speech
            min_speech_duration_ms: Minimum speech duration to trigger speech_start
            min_silence_duration_ms: Minimum silence duration to trigger speech_end
        """
        self.sample_rate = sample_rate
        self.speech_threshold = speech_threshold
        self.silence_threshold = silence_threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        
        # State tracking
        self.is_speaking = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.frames_per_ms = sample_rate / 1000
        
        # Load Silero VAD model
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load the Silero VAD model."""
        try:
            # Load pre-trained Silero VAD model
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.model.eval()
            logger.info("Silero VAD model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Silero VAD model: {e}")
            raise
    
    def process_audio_chunk(self, audio_chunk: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Process an audio chunk and return VAD decision.
        
        Args:
            audio_chunk: Audio data as numpy array (float32, shape: [samples])
            
        Returns:
            Tuple of (event_type, confidence) where:
            - event_type: 'speech_start', 'speech_end', or None
            - confidence: VAD confidence score (0.0 to 1.0)
        """
        if self.model is None:
            logger.error("VAD model is None!")
            return None, 0.0
            
        # Ensure audio is the right format
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)
            
        # Log audio chunk info
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        logger.info(f"🎯 Backend: VAD input: {len(audio_chunk)} samples, RMS: {rms:.4f}")
            
        # Convert to torch tensor
        audio_tensor = torch.from_numpy(audio_chunk)
        
        # Get VAD prediction
        with torch.no_grad():
            confidence = self.model(audio_tensor, self.sample_rate).item()
        
        logger.info(f"🧠 Backend: VAD raw confidence: {confidence:.4f}")
        
        # Apply hysteresis logic (pass chunk size for proper frame counting)
        event = self._apply_hysteresis(confidence, len(audio_chunk))
        
        if event:
            logger.info(f"🎯 VAD hysteresis triggered: {event} (confidence: {confidence:.4f})")
        
        return event, confidence
    
    def _apply_hysteresis(self, confidence: float, chunk_size: int) -> Optional[str]:
        """
        Apply hysteresis to prevent flickering between speech/silence states.
        
        Args:
            confidence: VAD confidence score
            chunk_size: Number of samples in the chunk
            
        Returns:
            Event type: 'speech_start', 'speech_end', or None
        """
        # Each chunk represents chunk_size samples (e.g., 512 samples at 16kHz = 32ms)
        chunk_duration_samples = chunk_size
        
        if confidence > self.speech_threshold:
            # Potential speech detected
            self.speech_frames += chunk_duration_samples
            self.silence_frames = 0
            
            # Check if we've had enough speech to trigger speech_start
            # frames_per_ms is actually samples_per_ms (sample_rate / 1000)
            min_speech_samples = self.min_speech_duration_ms * self.frames_per_ms
            logger.debug(f"📈 Speech accumulating: {self.speech_frames}/{min_speech_samples} samples (conf: {confidence:.3f} > {self.speech_threshold})")
            
            if not self.is_speaking and self.speech_frames >= min_speech_samples:
                self.is_speaking = True
                logger.info(f"🎤 Speech started: accumulated {self.speech_frames} samples (threshold: {min_speech_samples})")
                return 'speech_start'
                
        elif confidence < self.silence_threshold:
            # Potential silence detected
            self.silence_frames += chunk_duration_samples
            self.speech_frames = 0
            
            # Check if we've had enough silence to trigger speech_end
            min_silence_samples = self.min_silence_duration_ms * self.frames_per_ms
            logger.debug(f"📉 Silence accumulating: {self.silence_frames}/{min_silence_samples} samples (conf: {confidence:.3f} < {self.silence_threshold})")
            
            if self.is_speaking and self.silence_frames >= min_silence_samples:
                self.is_speaking = False
                logger.info(f"🔇 Speech ended: accumulated {self.silence_frames} samples of silence (threshold: {min_silence_samples})")
                return 'speech_end'
        else:
            # Confidence is between thresholds - maintain current state
            logger.debug(f"⏸️ VAD in hysteresis zone: {confidence:.3f} (between {self.silence_threshold} and {self.speech_threshold})")
        
        return None
    
    def reset_state(self):
        """Reset the VAD state (useful when starting a new session)."""
        self.is_speaking = False
        self.speech_frames = 0
        self.silence_frames = 0
        logger.info("VAD state reset")
