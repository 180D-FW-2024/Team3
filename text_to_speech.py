# Code from https://pypi.org/project/pyttsx3/
# pip install pyttsx3
# apt-get install espeak-ng

# https://rhasspy.github.io/piper-samples/
# Piper could be a good option to upgrade text to speech voice; currently sounds like it's from 2002

import pyttsx3

def tts(string):
    engine = pyttsx3.init()

    engine.setProperty('rate', 150)  

    engine.say(string)
    engine.runAndWait()
    engine.stop()