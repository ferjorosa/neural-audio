# Simple VAD Demo Frontend

React frontend for real-time Voice Activity Detection with WebSocket audio streaming.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# or
./start.sh
```

Frontend runs on `http://localhost:3001`

## How It Works

1. **Click "Start VAD"** → Request microphone access
2. **Audio capture** → OpusRecorder encodes microphone to Opus format
3. **WebSocket streaming** → Send audio chunks to backend in real-time
4. **Live feedback** → Display speech/silence status from VAD events

## Architecture

```
┌─────────────────┐   getUserMedia   ┌─────────────────┐
│   Microphone    │ ─────────────────► │ useAudioCapture │
└─────────────────┘                   │ • OpusRecorder  │
                                      │ • 40ms chunks   │
                                      └─────────────────┘
                                               │
                                               ▼
┌─────────────────┐   VAD Events     ┌─────────────────┐
│   UI Display    │ ◄───────────────  │ useWebSocket    │
│ • 🎤 SPEAKING   │                   │ • Send audio    │
│ • 🔇 SILENT     │   Audio chunks    │ • Receive events│
│ • Confidence    │ ─────────────────► │ • Auto-reconnect│
└─────────────────┘                   └─────────────────┘
```

## Code Structure

- **`src/app/page.tsx`** - Main UI component with VAD status display
- **`src/useAudioCapture.ts`** - Microphone access and Opus encoding
- **`src/useWebSocket.ts`** - WebSocket communication with backend
- **`public/`** - Opus encoder/decoder workers (copied from main project)

## Key Features

### Audio Capture
- **Opus encoding** at 24kHz for efficient streaming
- **40ms chunks** (960 samples) sent continuously
- **Echo cancellation** and auto-gain control enabled

### WebSocket Communication
- **Auto-reconnect** with exponential backoff
- **Base64 encoding** for binary audio data
- **Real-time** bidirectional communication

### UI Components
- **Start/Stop button** with connection status
- **Live VAD display** - 🎤 SPEAKING / 🔇 SILENT
- **Confidence meter** showing VAD probability
- **Event log** with timestamps

## WebSocket Messages

**Frontend → Backend:**
```typescript
{
  type: "audio_chunk",
  data: "base64_encoded_opus_data"
}
```

**Backend → Frontend:**
```typescript
{
  type: "vad_event",
  event: "speech_start" | "speech_end",
  confidence: number,
  timestamp: number
}
```

## Dependencies

- **Next.js 14** - React framework
- **OpusRecorder** - Real-time audio encoding
- **TypeScript** - Type safety
- **WebSocket API** - Real-time communication

## Browser Requirements

- Modern browser with WebRTC support
- Microphone access permissions
- WebSocket support
