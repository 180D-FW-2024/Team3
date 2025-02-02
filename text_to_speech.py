# Code from https://pypi.org/project/pyttsx3/
# pip install pyttsx3
# apt-get install espeak-ng

# https://rhasspy.github.io/piper-samples/
# Piper could be a good option to upgrade text to speech voice; currently sounds like it's from 2002

import io
import simpleaudio as sa
import wave
from piper import PiperVoice  # Assuming PiperVoice is imported from piper
import os

def say(string):

    dictionary = {
        "No recipe currently selected, ask for recipe suggestions to start a new recipe." : "no_recipe_selected.wav",
        "Error with measurement. Try again" : "measure_error.wav",
        "This step does not need a measurement." : "no_need_measurement.wav",
        "Adding allergy. State ingredient you are allergic to." : "allergy_add.wav",
        "Allergy addition failure." : "allergy_add_failure.wav",
        "Removing allergy. State ingredient you are not allergic to." : "allergy_remove.wav",
        "Allergy removal failure." : "allergy_remove_failure.wav",
        "Adding ingredient to inventory. State ingredient name, quantity, and measurement type." : "add_to_inv_instruction.wav",
        "Removing ingredient from inventory. State ingredient name, quantity, and measurement type." : "remove_from_inv_instruction.wav",
        "Generating recipe recommendation..." : "generating_recipe_rec.wav",
        "Recommendation Failure, Try again" : "recommendation_failure.wav",
        "Here is a list of recommended recipes, select 'Start' to begin or 'Next' to hear more" : "introduce_recipes.wav",
        "Recipe select failure, try again" : "recipe_select_failure.wav",
        "Invalid Command, say either 'Start' or 'Next'" : "invalid_command_recipe_rec.wav",
        "No recipe selected, returning to original recipe" : "return_to_og_recipe.wav",
        "Timer started" : "timer_started.wav",
        "Timer already running" : "timer_already_running.wav",
        "Timer paused" : "timer_paused.wav",
        "Timer not running" : "timer_not_running.wav",
        "Please place the ingredient on the scale and say: Hey Ratatouille, measure ingredient! when you're ready." : "scale_measurement.wav",
        "Recipe complete. Enjoy!" : "recipe_complete.wav",
        "Listening..." : "listening.wav",
        "Command not recognized" : "command_not_recognized.wav",
        "First step:" : "first_step.wav",
    }

    # Use prerecorded line if exists
    if string in dictionary:
        path = "voice_lines/" + dictionary[string]
        wave_obj = sa.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        return

    # Else tell user to wait while you create new voice clip using model
    path = "voice_lines/please_wait.wav"
    wave_obj = sa.WaveObject.from_wave_file(path)
    play_obj = wave_obj.play()

    model = "en_GB-alan-medium.onnx"
    voice = PiperVoice.load(model)

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

