# Code from https://pypi.org/project/pyttsx3/
# pip install pyttsx3
# apt-get install espeak-ng

# https://rhasspy.github.io/piper-samples/
# Piper could be a good option to upgrade text to speech voice; currently sounds like it's from 2002

# import pyttsx3

# def tts(string):
#     # engine = pyttsx3.init()

#     # voices = engine.getProperty('voices')
#     # for voice in voices:
#     #     print(voice)

#     # engine.setProperty('rate', 150)
#     # engine.setProperty('voice', 'english+f3')


#     # engine.say(string)
#     # engine.runAndWait()
#     # engine.stop()


from piper.voice import PiperVoice
import simpleaudio as sa
import tempfile
import os

def tts(string):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        temp_wav_path = temp_wav.name

    model = "en_GB-alan-medium.onnx"
    voice = PiperVoice.load(model)
    audio = voice.synthesize(string, temp_wav)

    # Play audio synchronously
    wave_obj = sa.WaveObject.from_wave_file(temp_wav_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

    os.remove(temp_wav_path)

# Example
tts("Hello, world!")

