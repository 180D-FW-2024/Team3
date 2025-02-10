# parse a "recipe" in string format

# instruction type (time, temperature, untimed, measurement, quantity, finish); value; string instruction
# ex: Timed; 300; Pan-fry for 5 minutes.

# example recipe string, based off https://www.allrecipes.com/recipe/12324/apple-pie-i/
# Quantity; 1; Prepare two 9-inch pie crusts and one 9-inch pie dish| Measurement; 150; Measure out 150 grams of white sugar| Measurement; 5.69; Measure out 5.69 grams of ground cinnamon| Quantity; 6; Prepare 6 cups of sliced apples| Measurement; 14; Measure out 14 grams of butter| 
# Temperature; 450; Gather the ingredients. Preheat the oven to 450 degrees F (230 degrees C)| Untimed; None; Line your 9-inch pie dish with one pastry crust. Set other one to the side| Untimed; None; Combine 3/4 cup sugar and cinnamon in a small bowl. Add more sugar if your apples are tart| Untimed; None; Layer apple slices in the prepared pie dish, sprinkling each layer with cinnamon-sugar mixture| Untimed; None; Dot top layer with small pieces of butter. Cover with top crust| 
# Timed; 600; Bake pie on the lowest rack of the preheated oven for 10 minutes| Timed; 1800; Reduce oven temperature to 350 degrees F (175 degrees C) and continue baking for about 30 minutes, until golden brown and filling bubbles| Finish; None; Serve!

# have each recipe class contain: array of instruction classes, int counter for which step the recipe is on, (ingredient list?)
# each instruction class has type, value, string instruction

# TTS import
from text_to_speech import tts as say

# HTTP Request import
import requests

import dotenv
import os

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Timer Class - courtesy of ChatGPT
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
import time
class CountdownTimer:
    def __init__(self, duration):
        # Initialize the timer with a given duration (in seconds).
        self.initial_duration = duration
        self.remaining_time = duration
        self.end_time = None
        self.running = False

    def set_time(self, seconds):
        # Set the countdown to start with a specific duration (in seconds).
        self.initial_duration = seconds
        self.remaining_time = seconds
        self.end_time = None
        self.running = False

    def start(self):
        # Start or resume the countdown.
        if not self.running:
            # Calculate the end time from now using the remaining time
            self.end_time = time.time() + self.remaining_time
            say("Timer started")
            self.running = True
        elif self.running:
            say("Timer already running")

    def pause(self):
        # Pause the countdown and save the remaining time.
        if self.running:
            self.remaining_time = max(0, self.end_time - time.time())
            say("Timer paused")
            self.running = False
        elif not self.running:
            say("Timer not running")

    def reset(self):
        # Reset the countdown to the initial duration.
        self.remaining_time = self.initial_duration
        self.end_time = None
        self.running = False

    def time_left(self):
        # Return the remaining time in the countdown.
        if self.running:
            self.remaining_time = max(0, self.end_time - time.time())
        return self.remaining_time

    def is_finished(self):
        # Check if the countdown has finished.
        return self.time_left() <= 0

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Instruction Class
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Step:
    def __init__(self, type, value, string):
        self.type = type
        self.value = value
        self.string = string
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Ingredient Class
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Ingredient:
    def __init__(self, name, quantity, measureType):
        self.name = name
        self.quantity = quantity
        self.measureType = measureType
    def __str__(self):
        if self.measureType == "Weight":
            return f"{self.quantity} gram{'s' if self.quantity > 1 else ''} {self.name}"
        elif self.measureType == "Volume":
            return f"{self.quantity} milliliter{'s' if self.quantity > 1 else ''} {self.name}"
        elif self.measureType == "Count":
            if self.quantity == 1:
                return f"{self.quantity} {self.name}"
            else:
                return f"{self.quantity} {self.name}s"
        return f"{self.quantity} {self.measureType} {self.name}"

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Recipe Class
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Recipe:
    # ------------------------------------------------------------------------
    # UTILITY FUNCTIONS
    # ------------------------------------------------------------------------

    # Initialize Recipe object with list of steps and counter = 0
    def __init__(self, recipeObject=None):
        if recipeObject is None:
            return
        recipeString = recipeObject["recipe_text"]
        recipeIngredients = recipeObject["ingredients"]
        self.steps = self.parseInstrString(recipeString)
        self.ingredients = self.parseIngredientsString(recipeIngredients)
        self.stepCounter = 0
        self.timer = CountdownTimer(0)
        self.finished = False

    # Destructor to remove timer if new recipe is started
    def __del__(self):
        if(self.timer.running):
            self.timer.reset()

    def parseInstrString(self, recipeString):
        # Prepare step list to later append to
        steps = []

        # Split recipe string into individual step strings
        strSteps = recipeString.split("| ")

        # For each string step, create a Step class with the fields from the string step
        for step in strSteps:
            stepFields = step.split("; ")
            steps.append(Step(stepFields[0], stepFields[1], stepFields[2]))

        # FOR DEBUGGING ----------------------------------------------------------------------------------------------------
        # for step in steps:
        #     print(step.type + "," + step.value + "," + step.string + '\n')
        # FOR DEBUGGING ----------------------------------------------------------------------------------------------------

        # Return list of instruction objects
        return steps

    def parseIngredientsString(self, recipeIngredients):
        ingredients = []
        for ingredient in recipeIngredients:
            if "measureType" not in ingredient or "quantity" not in ingredient or "name" not in ingredient:
                continue
            ingredients.append(Ingredient(ingredient["name"], ingredient["quantity"], ingredient["measureType"]))
        return ingredients

    # get string instruction for current step
    def getCurrentInstruction(self):
        return self.steps[self.stepCounter].string
    
    # increase step counter by 1
    def incrementStepCounter(self):
        if(self.stepCounter <= len(self.steps)-2):
            self.stepCounter += 1
            return 0
        else:
            return 1
    
    # decrease step counter by 1
    def decrementStepCounter(self):
        if(self.stepCounter > 0):
            self.stepCounter -= 1
            return 0
        else:
            return 1

    # Manages the different types of values; ex: for Timed type, set timer; for Measurement type, get weight reading
    def manageCurrentStep(self):
        step = self.steps[self.stepCounter]

        # if step is Timed type, set Recipe's timer to start at step's value
        if(step.type == "Timed"):
            self.timer.set_time(int(step.value))

        # WIP
        # if step is Measurement type, tell user to do measure command when they've placed item on the scale
        if(step.type == "Measurement"):
            say("Please place the ingredient on the scale and say: Hey Ratatouille, measure ingredient! when you're ready.")
        
        if (step.type == "Finish"):
            say("Recipe complete. Enjoy!")
            self.finished = True
    
    # ------------------------------------------------------------------------
    # END UTILITY FUNCTIONS
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # COMMAND-MAPPED FUNCTIONS
    # ------------------------------------------------------------------------
    def nextStep(self):
        self.incrementStepCounter()
        say(self.getCurrentInstruction())
        self.manageCurrentStep()

    def currentStep(self):
        say(self.getCurrentInstruction())
        self.manageCurrentStep()

    def previousStep(self):
        self.decrementStepCounter()
        say(self.getCurrentInstruction())
        self.manageCurrentStep()

    def timeRemaining(self):
        say(str(round((self.timer.time_left())//60)) + " minutes and " + str(round(self.timer.time_left()) % 60) + " seconds remaining")
    
    def startTimer(self):
        self.timer.start()
    
    def stopTimer(self):
        self.timer.pause()

    def resetTimer(self):
        self.timer.reset()

    def listIngredients(self):
        say("Ingredients: " + ", ".join([ing.__str__() for ing in self.ingredients]))

    def suggestRecipes(self):
        if self.userId is None:
            return None
        requests.get(backend_url + "/suggest-recipes", json={"user_id": self.userId})
    
    # ------------------------------------------------------------------------
    # END COMMAND-MAPPED FUNCTIONS
    # ------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------





