"""WebSocket message models for the VAD demo."""

from pydantic import BaseModel
from typing import Literal, Optional


class AudioChunkMessage(BaseModel):
    """Message sent from client with audio data."""
    type: Literal["audio_chunk"]
    data: str  # base64 encoded Opus data


class ResetMessage(BaseModel):
    """Message to reset VAD state."""
    type: Literal["reset"]


class VADEventMessage(BaseModel):
    """VAD event sent to client."""
    type: Literal["vad_event"]
    event: Literal["speech_start", "speech_end"]
    confidence: float
    timestamp: float


class VADConfidenceMessage(BaseModel):
    """Confidence update sent to client."""
    type: Literal["vad_confidence"]
    confidence: float
    is_speaking: bool


class ResetCompleteMessage(BaseModel):
    """Confirmation that reset was completed."""
    type: Literal["reset_complete"]
    message: str


# Union type for all client messages
ClientMessage = AudioChunkMessage | ResetMessage

# Union type for all server messages  
ServerMessage = VADEventMessage | VADConfidenceMessage | ResetCompleteMessage


class VADResult(BaseModel):
    """Result from VAD processing."""
    event: Optional[Literal["speech_start", "speech_end"]]
    confidence: float
