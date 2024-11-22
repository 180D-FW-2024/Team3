# Code from https://pypi.org/project/pyttsx3/
# pip install pyttsx3
# apt-get install espeak-ng

import pyttsx3

engine = pyttsx3.init()

engine.setProperty('rate', 125)  

engine.say("I will speak this text")
engine.runAndWait()
engine.stop()