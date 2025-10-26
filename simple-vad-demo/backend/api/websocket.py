"""WebSocket endpoint for real-time audio processing."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
import logging

from services.connection_service import ConnectionService
from models.messages import ClientMessage, AudioChunkMessage, ResetMessage

logger = logging.getLogger(__name__)

router = APIRouter()

# Shared connection service instance
connection_service = ConnectionService()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio processing.
    
    Expected message format:
    {
        "type": "audio_chunk",
        "data": "base64_encoded_opus_data"
    }
    
    Response message format:
    {
        "type": "vad_event",
        "event": "speech_start" | "speech_end",
        "confidence": 0.0-1.0,
        "timestamp": "timestamp"
    }
    """
    # Accept connection and create session
    session = await connection_service.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse and validate message
                message_dict = json.loads(data)
                logger.info(f"📨 Backend: Received WebSocket message: type={message_dict.get('type')}")
                
                # Route message based on type
                if message_dict.get("type") == "audio_chunk":
                    message = AudioChunkMessage(**message_dict)
                    await connection_service.handle_audio_chunk(websocket, message)
                    
                elif message_dict.get("type") == "reset":
                    message = ResetMessage(**message_dict)
                    await connection_service.handle_reset(websocket, message)
                    
                elif message_dict.get("type") == "test":
                    logger.info(f"🧪 Backend: Received test message: {message_dict.get('message')}")
                    
                else:
                    logger.warning(f"Unknown message type: {message_dict.get('type')}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                
            except ValidationError as e:
                logger.error(f"Invalid message format: {e}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        
    finally:
        connection_service.disconnect(websocket)
