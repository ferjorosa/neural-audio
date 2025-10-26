# Neural Audio

A collection of neural audio processing tools including speech-to-text, text-to-speech, and voice activity detection.

## Projects

### Frontend - Voice Activity Detection Web App
A React-based web application that uses advanced Voice Activity Detection (VAD) to accurately detect when a user is speaking.

**Features:**
- Real-time voice activity detection using [@ricky0123/vad-react](https://docs.vad.ricky0123.com/user-guide/react/)
- Much more accurate than simple volume thresholds
- Modern React + TypeScript + Vite setup
- Beautiful, responsive UI with real-time visual feedback

**Setup:**
```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173 in your browser.

### Python Demos
- `demos/stt_demo.py` - Speech-to-text demonstration
- `demos/tts_demo.py` - Text-to-speech demonstration

**Setup:**
```bash
uv sync
uv run python demos/stt_demo.py
```

## Development

This project uses:
- `uv` for Python dependency management
- `npm` for frontend JavaScript dependencies
- React + TypeScript + Vite for the web frontend

## Tunneling (for external access)
```bash
cloudflared tunnel --url http://localhost:5173
```