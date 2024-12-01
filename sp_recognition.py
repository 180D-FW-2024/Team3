# Boilerplate code taken from geeksforgeeks.org, modified in part by ChatGPT
# pip install SpeechRecognition
# sudo apt install python3-pyaudio
# pip install typing-extensions -u
# apt-get install portaudio19-dev python-all-dev
# pip install google-cloud-speech
# apt-get install flac

import speech_recognition as sr
from text_to_speech import tts as say
def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Adjusting for ambient noise, please wait...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for the wake word 'Hey Ratatouille'. Press Ctrl+C to stop.")

    try:
        while True:
            with mic as source:
                print("Waiting for 'Hey Ratatouille'...")
                audio = recognizer.listen(source, timeout=None)  # Listen indefinitely

            try:
                text = recognizer.recognize_google(audio, language="en")
                print(f"Heard: {text}")

                # Check if the wake word "Hey Ratatouille" is spoken
                if "hey ratatouille" in text.lower():  # Case insensitive check
                    say("Hello! Listening for your command...")
                    
                    # Listen for the command after the wake word
                    with mic as source:
                        audio_command = recognizer.listen(source, timeout=None)
                    
                    try:
                        command = recognizer.recognize_google(audio_command, language="en")
                        print(f"You said: {command}")
                        # Call command handler with command
                    except sr.UnknownValueError:
                        print("Sorry, I couldn't understand the command.")
                    except sr.RequestError as e:
                        print(f"Error with the speech recognition service: {e}")
                else:
                    print("No wake word detected, ignoring...")
            except sr.UnknownValueError:
                print("Could not understand audio, please try again.")
            except sr.RequestError as e:
                print(f"Error with the speech recognition service: {e}")

    except KeyboardInterrupt:
        print("\nListening stopped.")
        return

# Call the function
listen_and_respond()