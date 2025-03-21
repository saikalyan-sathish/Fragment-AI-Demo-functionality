import os
import pyaudio
import wave
import io
import numpy as np
import soundfile as sf
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("HF_API_KEY")

# Initialize Hugging Face Inference Client
client = InferenceClient(
    provider="hf-inference",
    api_key=API_KEY
)

# PyAudio Configuration
FORMAT = pyaudio.paInt16  # 16-bit format
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate in Hz
CHUNK = 1024  # Buffer size

def record_audio_pyaudio(duration=7):
    """Record audio from the microphone using PyAudio and store it in memory."""
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    input=True, frames_per_buffer=CHUNK)

    print(f"Recording for {duration} seconds...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording completed.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Convert recorded frames into WAV format in memory
    audio_buffer = io.BytesIO()
    with wave.open(audio_buffer, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return audio_buffer.getvalue()

def play_audio(audio_data):
    """Play back the recorded audio before sending it to the model."""
    p = pyaudio.PyAudio()
    audio_buffer = io.BytesIO(audio_data)

    with wave.open(audio_buffer, "rb") as wf:
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        print("Playing back recorded audio...")
        data = wf.readframes(CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()

def transcribe_audio(audio_data):
    """Send the in-memory audio data to Hugging Face Whisper API using InferenceClient."""
    # Convert bytes to numpy array and save as FLAC format in memory
    audio_buffer = io.BytesIO(audio_data)
    with wave.open(audio_buffer, "rb") as wf:
        sample_rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    # Convert audio to NumPy array
    audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

    # Save as FLAC in memory and extract raw bytes
    flac_buffer = io.BytesIO()
    sf.write(flac_buffer, audio_np, sample_rate, format="FLAC")
    flac_bytes = flac_buffer.getvalue()  # 🔥 Fix: Extract raw bytes

    # Send to Hugging Face Whisper model
    try:
        result = client.automatic_speech_recognition(flac_bytes, model="openai/whisper-large-v3")
        return result.get("text", "No transcription available")
    except Exception as e:
        return f"Error in transcription: {e}"

def get_voice_input():
    """Record audio in real-time, play it back, and return transcribed text."""
    audio_data = record_audio_pyaudio(duration=5)

    # Play the recorded audio before transcription
    play_audio(audio_data)

    return transcribe_audio(audio_data)
