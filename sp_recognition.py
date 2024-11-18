# Boilerplate code taken from geeksforgeeks.org
# Needs SpeechRecognition and PyAudio

import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak")
    audio_text = r.listen(source)
    
    try:
        # using google speech recognition
        print("Text: "+r.recognize_google(audio_text))
    except:
        print("Error")