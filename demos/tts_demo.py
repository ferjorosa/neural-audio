"""
Text-to-Speech Demo

This demo uses the `hexgrad/Kokoro-82M` model via the `kokoro` library to convert text into audio.

How it works:
1. User types or pastes text into the input box.
2. User clicks the "Synthesize" button.
3. The text is converted into speech using the `hexgrad/Kokoro-82M` model (default voice: 'en_us_male').
4. The synthesized audio is played back.

Required: 
- The `kokoro` library and its dependencies (automatically installed on first run)
- The `hexgrad/Kokoro-82M` model (automatically downloaded on first run)
- System dependency: `espeak-ng` (install with `sudo apt-get install espeak-ng`)
- The `KPipeline` is initialized with `lang_code='a'` for American English.
"""

import gradio as gr
from kokoro import KPipeline
import numpy as np
import torch

# Initialize the TTS pipeline for Kokoro with CUDA if available
try:
    if torch.cuda.is_available():
        print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name()}")
        # Clear any existing CUDA cache
        torch.cuda.empty_cache()
        tts_pipeline = KPipeline(lang_code='a', device='cuda')
    else:
        print("CUDA not available, using CPU")
        tts_pipeline = KPipeline(lang_code='a', device='cpu')
except Exception as e:
    print(f"Failed to initialize with CUDA: {e}")
    print("Falling back to CPU")
    tts_pipeline = KPipeline(lang_code='a', device='cpu')

def synthesize_speech(text):
    if not text:
        return None
    
    # Generate speech from the input text using the default voice
    generator = tts_pipeline(text, voice='af_heart')
    
    # Collect all audio chunks
    all_audio = []
    sampling_rate = 24000 # Kokoro's default sampling rate
    for i, (gs, ps, audio) in enumerate(generator):
        all_audio.append(audio)
    
    # Concatenate all audio chunks into a single numpy array
    if all_audio:
        combined_audio = np.concatenate(all_audio)
    else:
        return None # Return None if no audio was generated
    
    # Gradio expects a tuple of (sampling_rate, audio_data)
    return (sampling_rate, combined_audio)

# Create the Gradio interface
demo = gr.Interface(
    fn=synthesize_speech,
    inputs=gr.Textbox(lines=5, label="Enter Text Here"),
    outputs=gr.Audio(label="Synthesized Audio"),
    title="Text-to-Speech Synthesizer (Kokoro-82M)",
    description="Type some text and convert it into speech using the Kokoro-82M TTS model."
)

# Launch the Gradio demo
demo.launch()
