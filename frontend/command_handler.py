#------------------------------------------------------------------------------------------------------------------------------------------------------
# Helper functions for Ingredient Management
#------------------------------------------------------------------------------------------------------------------------------------------------------
from text_to_speech import tts as say
from typing import Optional
from recipe_handler import Recipe
from scale_reader import get_weight_in_grams
from thermometer_reader import get_current_temperature_f
from LLM.LLMAgent import answer_question, options
import requests
import speech_recognition as sr
import dotenv
import os

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

# imports here, so that this script can call the scripts it needs to
def handle_command(command, recipe_object) -> Optional[str]:
    if(command == "add ingredient"):
        return 'add ingredient'
    elif(command == "add ingredient with camera"):
        return 'add ingredient with camera'
    elif(command == "scan login"):
        return 'scan login'
    elif(command == "remove ingredient"):
        return 'remove ingredient'
    elif(command == "recommend recipe"):
        return 'recommend recipe'
    elif(command == "add allergy"):
        return 'add allergy'
    elif(command == "remove allergy"):
        return 'remove allergy'
    elif recipe_object is None:
        say("No recipe currently selected, ask for recipe suggestions to start a new recipe.")
        return None
    elif(command == "next instruction"):
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
        temperature = get_current_temperature_f()
        if(temperature is not None):
            say("The thermometer currently reads " + str(temperature) + " degrees fahrenheit.")
        else:
            say("Error with measurement. Try again")
        return
    elif(command == "measure ingredient"):
        # get weight from bluetooth scale and compare it to the required weight
        # if using a cup to hold ingredient, should calibrate scale using the cup such that with only the cup, the scale reads 0
        if(recipe_object.steps[recipe_object.stepCounter].type == "Measurement"):
            scaleMeasurement = get_weight_in_grams()
            if(scaleMeasurement is not None):
                if(0.95 < scaleMeasurement/int(recipe_object.steps[recipe_object.stepCounter].value) < 1.05):
                    say("Your measurement, " + str(scaleMeasurement) + " grams, is within 5 percent of the expected measurement. Feel free to move to the next step.")
                else:
                    say("Your measurement, " + str(scaleMeasurement) + " grams, is not within 5 percent of the expected measurement. Try again.")
            else:
                say("Error with measurement. Try again")
        else:
            say("This step does not need a measurement.")
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
    elif(command == "question"):
        return 'question'
    else:
        return None

def questionHandler(recognizer, recipe, source, userId):

    say("Please ask your question.")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        audio_command = recognizer.listen(source, timeout=None)
    try:
        # First, get the allergies and ingredients
        questionString = recognizer.recognize_google(audio_command, language="en")
        print("You said: " + questionString)
        say("Generating response...")

        
        while True:
            try:
                print("Retrying...")
                response = requests.get(backend_url + "/get-allergies-ingredients?userId=" + str(userId), timeout=5)
                if response.status_code == 200:  # Check if response is successful
                    break
            except requests.exceptions.RequestException:  # Catches timeout and other request errors
                pass  
        if response.status_code == 200:
            contextAllergies = response.json()['allergies']
            contextIngredients = response.json()['ingredients']
        else:
            contextAllergies = None
            contextIngredients = None
            
        print("Recipe: ", str(recipe))
        answer = answer_question(questionString, contextIngredients=contextIngredients, contextAllergies=contextAllergies, contextRecipe=str(recipe))

        if answer == "INVALID":
            say("I'm sorry, I couldn't answer your question.")
        else:
            print(answer)
            say(answer)
    
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the question.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")
    return


def addAllergyHandler(recognizer, recipe, source, userId):
    say("Adding allergy. State ingredient you are allergic to.")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        audio_command = recognizer.listen(source, timeout=None)
    try:
        ingredientString = recognizer.recognize_google(audio_command, language="en")
        print("You said: " + ingredientString)
        while True:
            try:
                print("Retrying...")
                response = requests.put(backend_url + "/add-allergy/" + str(userId) + "/" + ingredientString, timeout=5)
                if 200 <= response.status_code < 300:  # Check if response is successful
                    break
            except requests.exceptions.RequestException:  # Catches timeout and other request errors
                pass  
        
        if response.status_code == 200:
            say(f"{ingredientString} allergy was already added.")
            return
        elif response.status_code == 201:
            say(f"{ingredientString} allergy added")
        else:
            say("Allergy addition failure.")
        
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the ingredient.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")
    return


def removeAllergyHandler(recognizer, recipe, source, userId):
    say("Removing allergy. State ingredient you are not allergic to.")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        audio_command = recognizer.listen(source, timeout=None)
    try:
        ingredientString = recognizer.recognize_google(audio_command, language="en")
        print("You said: " + ingredientString)
        while True:
            try:
                print("Retrying...")
                response = requests.put(backend_url + "/remove-allergy/" + str(userId) + "/" + ingredientString, timeout=5)
                if 200 <= response.status_code < 300:  # Check if response is successful
                    break
            except requests.exceptions.RequestException:  # Catches timeout and other request errors
                pass  
        
        if response.status_code == 200:
            say(f"{ingredientString} allergy was removed.")
            return
        else:
            say("Allergy removal failure.")
        
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the ingredient.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")
    return

def addIngredientHandler(recognizer, recipe, source, userId):
    say("Adding ingredient to inventory. State ingredient name, quantity, and measurement type.")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    confirmation = False
    with mic as source:
        audio_command = recognizer.listen(source, timeout=None)
    try:
        ingredientString = recognizer.recognize_google(audio_command, language="en")
        print("You said: " + ingredientString)
        say("I heard " + ingredientString + ". Is this what you meant? If you'd like to cancel, say, cancel; otherwise, say yes or no.")
        with mic as confirmation_source:
            confirmation_audio_command = recognizer.listen(confirmation_source, timeout=None)
            confirmation_string = recognizer.recognize_google(confirmation_audio_command, language="en")
            if "yes" in confirmation_string.lower():
                confirmation = True
            elif "no" in confirmation_string.lower() or "cancel" in confirmation_string.lower():
                say("Cancelling ingredient addition.")
                return
            else:
                say("Couldn't understand your response. Cancelling ingredient addition.")
                return
        while confirmation:
            try:
                print("Retrying...")
                print(userId)
                response = requests.put(backend_url + "/add-ingredient/" + str(userId) + "/" + ingredientString, timeout=5)
                if response.status_code == 200:  # Check if response is successful
                    break
                if response.status_code != 200:
                    say("Addition Failure")
                    print("Addition Failure")
                    return
            except requests.exceptions.RequestException:  # Catches timeout and other request errors
                pass  
        say("Ingredient added to inventory. You now have " + response.json()['text'])
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the command.")
        say("Sorry, I couldn't understand the command.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")

def addIngredientCamHandler(recognizer, image_recognizer, recipe, source, userId):
    say("Place ingredient on the provided placement paper. When you have done so, say: Ready!")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        audio = recognizer.listen(source, timeout=None)
    try:
        # Wait for user to ready their ingredient
        response = recognizer.recognize_google(audio, language="en")
        print("You said: " + response)
        if "ready" in response.lower():
            image_recognizer.take_pic()
            return_val = image_recognizer.predict_img()
            print(return_val)
            if(type(return_val) == tuple):
                if(return_val[0] == 6):
                    missing_corners = return_val[1]
                    missing_str = ""
                    for corner in missing_corners:
                        missing_str += 'corner ' + str(corner) + ', '
                    say("The following corners are not within the camera's frame: " + missing_str + ". Realign the paper and ingredient and try again.")
                else:
                    say("Error with image recognition. Please try again.")
            else:
                # if not tuple, no error
                # Ask user for how many of the ingredient they want to add
                ingredientScalar = ""
                say("How much of this ingredient would you like to add?")
                with mic as scalar_source:
                    secondAudio = recognizer.listen(scalar_source, timeout=None)
                try:
                    ingredientScalar = recognizer.recognize_google(secondAudio, language="en")
                    print(ingredientScalar)
                except sr.UnknownValueError:
                    print("Sorry, I couldn't understand the command.")
                    say("Sorry, I couldn't understand what number you said. Cancelling ingredient addition.")
                    return

                # Add ingredient to database
                ingredientString = ingredientScalar + " " + return_val
                while True:
                    try:
                        print("Retrying...")
                        print(userId)
                        response = requests.put(backend_url + "/add-ingredient/" + str(userId) + "/" + ingredientString, timeout=5)
                        if response.status_code == 200:  # Check if response is successful
                            break
                        if response.status_code != 200:
                            say("Ingredient addition failure")
                            print("Addition Failure")
                            return    
                    except requests.exceptions.RequestException:  # Catches timeout and other request errors
                        pass    
                say("Ingredient added to inventory. You now have " + response.json()['text'])  
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the command.")
        say("Sorry, I couldn't understand the command.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")



def removeIngredientHandler(recognizer, recipe, source, userId):
    say("Removing ingredient from inventory. State ingredient name, quantity, and measurement type.")
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    confirmation = False
    with mic as source:
        audio_command = recognizer.listen(source, timeout=None)
    try:
        ingredientString = recognizer.recognize_google(audio_command, language="en")
        print("You said: " + ingredientString)
        say("I heard " + ingredientString + ". Is this what you meant? If you'd like to cancel, say, cancel; otherwise, say yes or no.")
        with mic as confirmation_source:
            confirmation_audio_command = recognizer.listen(confirmation_source, timeout=None)
            confirmation_string = recognizer.recognize_google(confirmation_audio_command, language="en")
            if "yes" in confirmation_string.lower():
                confirmation = True
            elif "no" in confirmation_string.lower() or "cancel" in confirmation_string.lower():
                say("Cancelling ingredient addition.")
                return
            else:
                say("Couldn't understand your response. Cancelling ingredient removal.")
                return
        while confirmation:
            try:
                print("Retrying...")
                response = requests.put(backend_url + "/remove-ingredient/" + str(userId) + "/" + ingredientString, timeout=5)
                if response.status_code == 200:  # Check if response is successful
                    break
                if response.status_code != 200:
                    print("Removal Failure")
                    say("Removal failure.")
                    return
            except requests.exceptions.RequestException:  # Catches timeout and other request errors
                pass  
        say("Ingredient removed from inventory. You now have: " + response.json()['text'])
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the command.")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")

def loadRecipe(recipeId):
    while True:
        try:
            print("Retrying...")
            response = requests.get(backend_url + "/get-recipe/" + str(recipeId), timeout=5)
            if 200 <= response.status_code < 300:  # Check if response is successful
                break
        except requests.exceptions.RequestException:  # Catches timeout and other request errors
            pass  
    
    if response.status_code != 200:
        return None
    return response.json()

def recommendRecipeHandler(recognizer, recipe, mic, userId):
    say("Generating recipe recommendation...")
    while True:
        try:
            print("Retrying...")
            response = requests.get(backend_url + "/suggest-recipes/" + str(userId), timeout=5)
            if 200 <= response.status_code < 300:  # Check if response is successful
                break
            if response.status_code != 200:
                print("Recommendation Failure")
                say("Recommendation Failure, Try again")
                return None
        except requests.exceptions.RequestException:  # Catches timeout and other request errors
            pass  

    if response.json() == []:
        say("No recipes found")
        return None
    data = response.json()
    say("Here is a list of recommended recipes, select 'Start' to begin or 'Next' to hear more")
    for recipe in data:
        say("Recipe title: " + recipe['title'] + ". Completion time: " + str(recipe['completion_time']//60) + " minutes")
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
            if "start" in command.lower():
                recipe_response = loadRecipe(recipe['id'])
                if recipe_response is None:
                    say("Recipe select failure, try again")
                    return None
                print(recipe_response)
                say("Recipe selected: " + recipe_response['title'])
                return recipe_response
            elif "next" in command.lower():
                break
            elif "cancel" in command.lower():
                say("No recipe selected, cancelling recipe selection.")
                return None
            else:
                say("Invalid Command, say either 'Start', 'Next', or 'Cancel'.")

    say("No more available recipes based on your ingredient list. Cancelling recipe selection.")
    return None