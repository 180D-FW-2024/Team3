# Code from https://pypi.org/project/pyttsx3/
# pip install pyttsx3
# apt-get install espeak-ng

# https://rhasspy.github.io/piper-samples/
# Piper could be a good option to upgrade text to speech voice; currently sounds like it's from 2002

import wave
import os
import simpleaudio as sa
from piper import PiperVoice  # Assuming PiperVoice is imported from piper

import io
import simpleaudio as sa
import wave
from piper import PiperVoice  # Assuming PiperVoice is imported from piper

def say(string):
    model = "en_GB-alan-medium.onnx"
    voice = PiperVoice.load(model)
    wav_filename = "output.wav"

    # Use an in-memory buffer instead of writing to a file
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, "wb") as wav_file:
        voice.synthesize(string, wav_file)
    
    # Extract raw audio data for playback
    wav_buffer.seek(0)  # Reset buffer position
    with wave.open(wav_buffer, "rb") as wav_file:
        audio_data = wav_file.readframes(wav_file.getnframes())
        sample_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()

    # Play audio directly from memory
    play_obj = sa.play_buffer(audio_data, num_channels, sample_width, sample_rate)
    play_obj.wait_done()  # Wait until playback finishes

    os.remove(wav_filename)
