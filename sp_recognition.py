# Boilerplate code taken from geeksforgeeks.org, modified in part by ChatGPT
# pip install SpeechRecognition
# sudo apt install python3-pyaudio
# pip install typing-extensions -u
# apt-get install portaudio19-dev python-all-dev
# pip install google-cloud-speech
# apt-get install flac
# pip install sounddevice

import speech_recognition as sr
from text_to_speech import tts as say
from command_handler import handle_command, addIngredientHandler, recommendRecipeHandler
from recipe_handler import Recipe

import dotenv
import requests
import os
import sounddevice

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

# for testing; handle_command(recommend_recipe) should be called by listen_and_respond when the command is heard, and should return a Recipe object to replace the current Recipe object
test = "Quantity; 1; Prepare two 9-inch pie crusts and one 9-inch pie dish| Measurement; 150; Measure out 150 grams of white sugar| Measurement; 5.69; Measure out 5.69 grams of ground cinnamon| Quantity; 6; Prepare 6 cups of sliced apples| Measurement; 14; Measure out 14 grams of butter| Temperature; 450; Gather the ingredients. Preheat the oven to 450 degrees F (230 degrees C)| Untimed; None; Line your 9-inch pie dish with one pastry crust. Set other one to the side| Untimed; None; Combine 3/4 cup sugar and cinnamon in a small bowl. Add more sugar if your apples are tart| Untimed; None; Layer apple slices in the prepared pie dish, sprinkling each layer with cinnamon-sugar mixture| Untimed; None; Dot top layer with small pieces of butter. Cover with top crust| Timed; 600; Bake pie on the lowest rack of the preheated oven for 10 minutes| Timed; 1800; Reduce oven temperature to 350 degrees F (175 degrees C) and continue baking for about 30 minutes, until golden brown and filling bubbles| Finish; None; Serve!"
jsonTest = {
    "completion_time": 0,
    "id": 1,
    "ingredients": [
        {
            "id": 1,
            "measureType": "Count",
            "name": "pie crusts",
            "quantity": 1
        },
        {
            "id": 2,
            "measureType": "Count",
            "name": "pie dish",
            "quantity": 1
        },
        {
            "id": 3,
            "measureType": "Weight",
            "name": "sugar",
            "quantity": 150
        },
        {
            "id": 4,
            "measureType": "Weight",
            "name": "ground cinnamon",
            "quantity": 5.69
        },
        {
            "id": 5,
            "measureType": "Count",
            "name": "sliced apples",
            "quantity": 6
        },
        {
            "id": 6,
            "measureType": "Weight",
            "name": "butter",
            "quantity": 14
        }
    ],
    "recipe_text": test,
    "scale_needed": 0,
    "thermometer_needed": 0,
    "title": "Test Recipe"
}
recipe = Recipe(jsonTest)
# jump to 10 min pie bake step
for x in range(10):
    recipe.incrementStepCounter()


# Looping listener
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
                audio = recognizer.listen(source, timeout=None)  # Listen indefinitely

            try:
                text = recognizer.recognize_google(audio, language="en")
                print(f"Heard: {text}")

                # Check if the wake word "Hey Ratatouille" is spoken
                if "hey ratatouille" in text.lower():  # Case insensitive check
                    say("Listening for your command")
                    
                    # Listen for the command after the wake word
                    with mic as source:
                        audio_command = recognizer.listen(source, timeout=None)
                    
                    try:
                        command = recognizer.recognize_google(audio_command, language="en")
                        print(f"You said: {command}")

                        command = requests.get(backend_url + "/command/" + command)
                        if command.status_code != 200:
                            print("Command not recognized")
                            continue
                        
                        # Call command handler with command
                        additionalPrompt = handle_command(command.json()['response'].lower(), recipe)
                        if additionalPrompt is not None:
                            if additionalPrompt == 'add ingredient':
                                addIngredientHandler(recognizer, recipe, source)
                            elif additionalPrompt == 'recommend recipe':
                                recipe_response = recommendRecipeHandler(recognizer, recipe, mic)
                                if recipe_response is not None:
                                    print("Recipe response: ", recipe_response)
                                    recipe = Recipe(recipe_response)
                        
                        # handle_command(command, recipe)

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