# Boilerplate code taken from geeksforgeeks.org
# pip install SpeechRecognition
# sudo apt install python3-pyaudio
# pip install typing-extensions -u
# apt-get install portaudio19-dev python-all-dev
# pip install google-cloud-speech
# apt-get install flac

import speech_recognition as sr

r = sr.Recognizer()


with sr.Microphone() as source:
    print("Adjusting for ambient noise; please wait a few seconds...")
    r.adjust_for_ambient_noise(source, duration = 2)
    print("Speak!")
    audio_text = r.listen(source)
    
    try:
        # using google speech recognition
        print("Text: "+r.recognize_google(audio_text))
    except:
        print("Error")