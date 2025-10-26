# Simple VAD Demo

Real-time Voice Activity Detection using Silero VAD. Click a button, start talking, and see when the system detects speech vs silence.

## 🎯 What This Demo Does

- **Frontend**: Captures microphone audio using Opus encoding and streams it via WebSocket
- **Backend**: Receives audio stream, processes it with Silero VAD, and sends back speech/silence events
- **Real-time Feedback**: Shows live voice activity status with confidence scores

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket     ┌─────────────────┐
│   React Frontend│ ◄──────────────► │ Python Backend  │
│                 │                  │                 │
│ • Audio Capture │    Opus Audio    │ • FastAPI       │
│ • OpusRecorder  │ ──────────────►  │ • Silero VAD    │
│ • WebSocket     │                  │ • Audio Processing│
│ • UI Display    │ ◄──────────────  │ • Event Emission│
└─────────────────┘   VAD Events     └─────────────────┘
```

### Audio Flow

1. **Capture**: Browser captures microphone audio at 24kHz
2. **Encode**: OpusRecorder encodes audio to Opus format (efficient streaming)
3. **Stream**: WebSocket sends base64-encoded Opus chunks to backend
4. **Decode**: Backend decodes Opus to PCM audio
5. **Resample**: Audio is resampled from 24kHz to 16kHz (Silero VAD requirement)
6. **Detect**: Silero VAD processes audio and returns speech probability
7. **Filter**: Hysteresis logic prevents flickering between speech/silence
8. **Notify**: Backend sends VAD events back to frontend

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ with [uv](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 16+ with npm

### Option 1: Run Everything Together

```bash
./start-demo.sh
```

Then open http://localhost:3001

### Option 2: Run Individually

**Backend:**
```bash
cd backend
./start.sh
# Backend runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend  
./start.sh
# Frontend runs on http://localhost:3001
```

## How It Works

1. **Frontend** captures microphone audio and streams it via WebSocket
2. **Backend** processes audio with Silero VAD and detects speech/silence
3. **UI** shows real-time feedback: 🎤 SPEAKING or 🔇 SILENT

## Project Structure

```
simple-vad-demo/
├── backend/           # Python FastAPI + Silero VAD
│   ├── main.py
│   ├── vad_processor.py
│   └── pyproject.toml
├── frontend/          # React + WebSocket client
│   ├── src/
│   └── package.json
└── start-demo.sh      # Run both together
```

That's it! A simple demo showing real-time voice activity detection.