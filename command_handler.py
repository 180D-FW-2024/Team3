#------------------------------------------------------------------------------------------------------------------------------------------------------
# Helper functions for Ingredient Management
#------------------------------------------------------------------------------------------------------------------------------------------------------
from text_to_speech import tts as say
import dotenv
import os

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

def addIngredient():
    say("Adding ingredient to inventory.")
    say("State ingredient type.")
    say("State measure type from Weight, Volume, Count.")
    say("State ingredient quantity.")
    pass

# imports here, so that this script can call the scripts it needs to
def handle_command(command, recipe_object):
    if(command == "next instruction"):
        recipe_object.nextStep()
    elif(command == "previous instruction"):
        recipe_object.previousStep()
    elif(command == "repeat instruction"):
        recipe_object.currentStep()
    elif(command == "list ingredients"):
        recipe_object.listIngredients() # UNTESTED
    elif(command == "current temperature"):
        return
    elif(command == "measure ingredient"):
        # get weight from bluetooth scale and compare it to the required weight
        # if using a cup to hold ingredient, should calibrate scale using the cup such that with only the cup, the scale reads 0
        return
    elif(command == "time remaining"):
        recipe_object.timeRemaining()
    elif(command == "start timer"):
        recipe_object.startTimer()
    elif(command == "stop timer"):
        recipe_object.stopTimer()
    elif(command == "add ingredient"):
        addIngredient()
    elif(command == "remove ingredient"):
        return
    elif(command == "recommend recipe"):
        return
    