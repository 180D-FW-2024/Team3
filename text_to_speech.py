# Code from https://pypi.org/project/pyttsx3/
# pip install pyttsx3
# apt-get install espeak-ng

import pyttsx3

def tts(string):
    engine = pyttsx3.init()

    engine.setProperty('rate', 125)  

    engine.say(string)
    engine.runAndWait()
    engine.stop()