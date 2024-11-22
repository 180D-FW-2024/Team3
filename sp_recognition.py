# Boilerplate code taken from geeksforgeeks.org
# pip install SpeechRecognition
# sudo apt install python3-pyaudio
# pip install typing-extensions -u
# apt-get install portaudio19-dev python-all-dev
# pip install google-cloud-speech
# apt-get install flac

import speech_recognition as sr

def translate_and_print():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Adjusting for ambient noise, please wait...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Start speaking. Press Ctrl+C to stop.")

    try:
        while True:
            with mic as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=None)  # No timeout
                
            try:
                text = recognizer.recognize_google(audio, language="en")
                print("You said:", text)
                # Translation logic can be added here if needed
            except sr.UnknownValueError:
                print("Could not understand audio, please try again.")
            except sr.RequestError as e:
                print("Error with the speech recognition service:", e)

    except KeyboardInterrupt:
        print("\nListening stopped.")
        return

# Call the function
translate_and_print()