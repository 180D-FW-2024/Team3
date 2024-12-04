#------------------------------------------------------------------------------------------------------------------------------------------------------
# Helper functions for Ingredient Management
#------------------------------------------------------------------------------------------------------------------------------------------------------
from text_to_speech import tts as say
from typing import Optional
from recipe_handler import Recipe
import requests
import speech_recognition as sr
import dotenv
import os

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

# imports here, so that this script can call the scripts it needs to
def handle_command(command, recipe_object) -> Optional[str]:
    if recipe_object is None:
        say("No recipe currently selected, ask for recipe suggestions to start a new recipe.")
        return None
    if(command == "next instruction"):
        recipe_object.nextStep()
        return None
    elif(command == "previous instruction"):
        recipe_object.previousStep()
        return None
    elif(command == "repeat instruction"):
        recipe_object.currentStep()
        return None
    elif(command == "list ingredients"):
        recipe_object.listIngredients() # UNTESTED
        return None
    elif(command == "current temperature"):
        return
    elif(command == "measure ingredient"):
        # get weight from bluetooth scale and compare it to the required weight
        # if using a cup to hold ingredient, should calibrate scale using the cup such that with only the cup, the scale reads 0
        return
    elif(command == "time remaining"):
        recipe_object.timeRemaining()
        return None
    elif(command == "start timer"):
        recipe_object.startTimer()
        return None
    elif(command == "stop timer"):
        recipe_object.stopTimer()
        return None
    elif(command == "add ingredient"):
        return 'add ingredient'
    elif(command == "remove ingredient"):
        return 'remove ingredient'
    elif(command == "recommend recipe"):
        return 'recommend recipe'

def addIngredientHandler(recognizer, recipe, source, userId):
    say("Adding ingredient to inventory. State ingredient name, quantity, and measurement type.")
    audio_command = recognizer.listen(source, timeout=None)
    try:
        ingredientString = recognizer.recognize_google(audio_command, language="en")
        print("You said: " + ingredientString)
        response = requests.put(backend_url + "/add-ingredient/" + str(userId) + "/" + ingredientString)
        if response.status_code != 200:
            print("Addition Failure")
            return
        else:
            say("Ingredient added to inventory:", response.json()['text'])
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the command.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")

def removeIngredientHandler(recognizer, recipe, source, userId):
    say("Removing ingredient from inventory. State ingredient name, quantity, and measurement type.")
    audio_command = recognizer.listen(source, timeout=None)
    try:
        ingredientString = recognizer.recognize_google(audio_command, language="en")
        print("You said: " + ingredientString)
        response = requests.put(backend_url + "/remove-ingredient/" + str(userId) + "/" + ingredientString)
        if response.status_code != 200:
            print("Removal Failure")
            return
        else:
            say("Ingredient removed from inventory:", response.json()['text'])
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the command.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")

def loadRecipe(recipeId):
    response = requests.get(backend_url + "/get-recipe/" + str(recipeId))
    if response.status_code != 200:
        return None
    return response.json()

def recommendRecipeHandler(recognizer, recipe, mic, userId):
    say("Generating recipe recommendation...")
    response = requests.get(backend_url + "/suggest-recipes/" + str(userId))
    if response.status_code != 200:
        print("Recommendation Failure")
        say("Recommendation Failure, Try again")
        return None
    else:
        if response.json() == []:
            say("No recipes found")
            return None
        data = response.json()
        say("Here is a list of recommended recipes, select 'Start' to begin or 'Next' to hear more")
        for recipe in data:
            say("Recipe title: " + recipe['title'] + ". Completion time: " + str(recipe['completion_time']) + " minutes")
            while True:
                with mic as source:
                    audio_command = recognizer.listen(source, timeout=None)
                try:
                    command = recognizer.recognize_google(audio_command, language="en")
                except sr.UnknownValueError:
                    print("Sorry, I couldn't understand the command.")
                    continue
                except sr.RequestError as e:
                    print(f"Error with the speech recognition service: {e}")
                    break
                if command.lower() == "start":
                    recipe_response = loadRecipe(recipe['id'])
                    if recipe_response is None:
                        say("Recipe select failure, try again")
                        return None
                    print(recipe_response)
                    say("Recipe selected: " + recipe_response['title'])
                    return recipe_response
                elif command.lower() == "next":
                    break
                else:
                    say("Invalid Command, say either 'Start' or 'Next'")

        say("No recipe selected, returning to original recipe")
        return None