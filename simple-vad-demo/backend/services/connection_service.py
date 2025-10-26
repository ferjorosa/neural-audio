"""WebSocket connection management service."""

import json
import base64
import asyncio
from typing import Dict
from fastapi import WebSocket
import logging

from services.audio_service import AudioService
from services.vad_service import VADService
from models.messages import (
    ClientMessage, AudioChunkMessage, ResetMessage,
    VADEventMessage, VADConfidenceMessage, ResetCompleteMessage
)

logger = logging.getLogger(__name__)


class AudioSession:
    """Represents an active audio processing session."""
    
    def __init__(self):
        self.audio_service = AudioService()
        self.vad_service = VADService()
        
    def reset(self):
        """Reset both audio and VAD state."""
        self.audio_service.reset()
        self.vad_service.reset()


class ConnectionService:
    """Manages WebSocket connections and audio sessions."""
    
    def __init__(self):
        self.active_sessions: Dict[WebSocket, AudioSession] = {}
        
    async def connect(self, websocket: WebSocket) -> AudioSession:
        """
        Accept a new WebSocket connection and create session.
        
        Args:
            websocket: The WebSocket connection
            
        Returns:
            Created audio session
        """
        await websocket.accept()
        session = AudioSession()
        self.active_sessions[websocket] = session
        
        logger.info(f"New connection established. Total: {len(self.active_sessions)}")
        return session
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection and cleanup session.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.active_sessions:
            del self.active_sessions[websocket]
        
        logger.info(f"Connection closed. Total: {len(self.active_sessions)}")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        """
        Send a message to a WebSocket connection.
        
        Args:
            websocket: Target WebSocket connection
            message: Message dictionary to send
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def handle_audio_chunk(self, websocket: WebSocket, message: AudioChunkMessage):
        """
        Process an audio chunk message.
        
        Args:
            websocket: Source WebSocket connection
            message: Audio chunk message
        """
        session = self.active_sessions.get(websocket)
        if not session:
            logger.error("No session found for WebSocket")
            return
            
        try:
            # Decode base64 audio data
            opus_data = base64.b64decode(message.data)
            logger.debug(f"📥 Backend: Received audio chunk: {len(opus_data)} bytes")
            logger.debug(f"📥 Backend: First 10 bytes (hex): {' '.join(f'{b:02x}' for b in opus_data[:10])}")
            
            # Process audio
            audio_16k = session.audio_service.process_opus_chunk(opus_data)
            if audio_16k is None:
                logger.warning("⚠️ Backend: Audio processing returned None")
                return
                
            logger.debug(f"🔊 Backend: Processed audio: {len(audio_16k)} samples at 16kHz")
                
            # Process with VAD
            vad_result = await session.vad_service.process_audio(audio_16k)
            
            # Only log when we have actual VAD results (not just buffering)
            if vad_result.confidence > 0.0:
                logger.info(f"VAD result: confidence={vad_result.confidence:.3f}, event={vad_result.event}, is_speaking={session.vad_service.is_speaking}")
            
            # Send VAD event if there's a state change
            if vad_result.event:
                logger.info(f"🎤 VAD EVENT: {vad_result.event} (confidence: {vad_result.confidence:.3f})")
                event_msg = VADEventMessage(
                    type="vad_event",
                    event=vad_result.event,
                    confidence=vad_result.confidence,
                    timestamp=asyncio.get_event_loop().time()
                )
                await self.send_message(websocket, event_msg.model_dump())
            
            # Send confidence updates for active audio
            if vad_result.confidence > 0.1:
                confidence_msg = VADConfidenceMessage(
                    type="vad_confidence",
                    confidence=vad_result.confidence,
                    is_speaking=session.vad_service.is_speaking
                )
                await self.send_message(websocket, confidence_msg.model_dump())
                
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
    
    async def handle_reset(self, websocket: WebSocket, message: ResetMessage):
        """
        Handle a reset request.
        
        Args:
            websocket: Source WebSocket connection
            message: Reset message
        """
        session = self.active_sessions.get(websocket)
        if not session:
            logger.error("No session found for WebSocket")
            return
            
        try:
            # Reset session state
            session.reset()
            
            # Send confirmation
            reset_msg = ResetCompleteMessage(
                type="reset_complete",
                message="VAD state reset successfully"
            )
            await self.send_message(websocket, reset_msg.model_dump())
            
        except Exception as e:
            logger.error(f"Error handling reset: {e}")
    
    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_sessions)
