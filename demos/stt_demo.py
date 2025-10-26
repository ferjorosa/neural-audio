"""
Audio Transcription Demo

This demo uses a Hugging Face `automatic-speech-recognition` pipeline to transcribe audio from a microphone into text.

How it works:
1. User clicks the microphone button to start recording
2. User speaks into the microphone
3. User clicks stop to end the recording
4. The audio is transcribed using the specified Hugging Face model (default: Whisper-base.en)
5. The transcribed text is displayed in the output

The demo uses a simple recording workflow rather than streaming to avoid:
- Transcribing silence/noise between words
- FFmpeg decoding errors from incomplete audio chunks
- Long-form generation issues with accumulating audio streams

Required: The `openai/whisper-base.en` Hugging Face model (automatically downloaded on first run).
"""

import gradio as gr
from transformers import pipeline
import torch

# Initialize the ASR pipeline with CUDA if available
try:
    if torch.cuda.is_available():
        print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name()}")
        device = 0  # Use first CUDA device
        transcriber = pipeline("automatic-speech-recognition", 
                             model="openai/whisper-base.en", 
                             device=device)
        print(f"ASR pipeline initialized on GPU")
    else:
        print("CUDA not available, using CPU")
        transcriber = pipeline("automatic-speech-recognition", 
                             model="openai/whisper-base.en")
except Exception as e:
    print(f"Failed to initialize with CUDA: {e}")
    print("Falling back to CPU")
    transcriber = pipeline("automatic-speech-recognition", 
                         model="openai/whisper-base.en")

def transcribe(audio):
    if audio is None:
        return "No audio provided"

    # Transcribe the audio
    result = transcriber(audio)

    # Extract text from the result
    if isinstance(result, dict):
        text = result.get("text", "")
    else:
        text = str(result)

    return text

demo = gr.Interface(
    fn=transcribe,
    inputs=gr.Audio(sources=["microphone"], type="filepath"),
    outputs="text",
    title="Audio Transcription",
    description="Record audio from your microphone and transcribe it to text"
)

demo.launch()
