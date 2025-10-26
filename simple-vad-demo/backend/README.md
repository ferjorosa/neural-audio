# Simple VAD Demo Backend

Real-time Voice Activity Detection backend using FastAPI and Silero VAD.

## Quick Start

```bash
# Install dependencies
uv sync

# Start server
uv run python main.py
# or
./start.sh
```

Server runs on `http://localhost:8000` with WebSocket at `ws://localhost:8000/ws`

## How It Works

1. **WebSocket receives** Opus-encoded audio chunks from frontend
2. **AudioService decodes** Opus → PCM and resamples 24kHz → 16kHz  
3. **VADService processes** audio with Silero VAD model
4. **ConnectionService sends** speech/silence events back to frontend

## Architecture

```
┌─────────────┐   Opus Audio   ┌─────────────────┐
│  Frontend   │ ──────────────► │ AudioService    │
│             │                 │ • Decode Opus   │
│             │                 │ • Resample      │
│             │                 └─────────────────┘
│             │                          │
│             │                          ▼
│             │                 ┌─────────────────┐
│             │                 │ VADService      │
│             │                 │ • Silero VAD    │
│             │                 │ • Hysteresis    │
│             │                 └─────────────────┘
│             │                          │
│             │   VAD Events    ┌─────────────────┐
│             │ ◄────────────── │ ConnectionService│
└─────────────┘                 │ • WebSocket     │
                                │ • Session Mgmt  │
                                └─────────────────┘
```

## Code Structure

- **`main.py`** - FastAPI app setup and routing
- **`api/`** - HTTP and WebSocket endpoints
- **`services/`** - Business logic (audio, VAD, connections)
- **`models/`** - Pydantic message models

## WebSocket Protocol

**Client → Server:**
```json
{"type": "audio_chunk", "data": "base64_opus_data"}
{"type": "reset"}
```

**Server → Client:**
```json
{"type": "vad_event", "event": "speech_start", "confidence": 0.85}
{"type": "vad_confidence", "confidence": 0.42, "is_speaking": false}
```

## Dependencies

- **FastAPI** - Web framework
- **Silero VAD** - Voice activity detection
- **OpusLib** - Audio codec
- **PyTorch** - ML framework for VAD model
