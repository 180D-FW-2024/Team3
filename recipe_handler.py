# parse a "recipe" in string format

# instruction type (time, temperature, untimed, measurement, quantity, finish); value; string instruction
# ex: Timed; 300; Pan-fry for 5 minutes.

# example recipe string, based off https://www.allrecipes.com/recipe/12324/apple-pie-i/
# Quantity; 1; Prepare two 9-inch pie crusts and one 9-inch pie dish| Measurement; 150; Measure out 150 grams of white sugar| Measurement; 5.69; Measure out 5.69 grams of ground cinnamon| Quantity; 6; Prepare 6 cups of sliced apples| Measurement; 14; Measure out 14 grams of butter| 
# Temperature; 450; Gather the ingredients. Preheat the oven to 450 degrees F (230 degrees C)| Untimed; None; Line your 9-inch pie dish with one pastry crust. Set other one to the side| Untimed; None; Combine 3/4 cup sugar and cinnamon in a small bowl. Add more sugar if your apples are tart| Untimed; None; Layer apple slices in the prepared pie dish, sprinkling each layer with cinnamon-sugar mixture| Untimed; None; Dot top layer with small pieces of butter. Cover with top crust| 
# Timed; 600; Bake pie on the lowest rack of the preheated oven for 10 minutes| Timed; 1800; Reduce oven temperature to 350 degrees F (175 degrees C) and continue baking for about 30 minutes, until golden brown and filling bubbles| Finish; None; Serve!

# have each recipe class contain: array of instruction classes, int counter for which step the recipe is on, (ingredient list?)
# each instruction class has type, value, string instruction

from text_to_speech import say

# Instruction Class
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Step:
    def __init__(self, type, value, string):
        self.type = type
        self.value = value
        self.string = string
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Recipe Class
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Recipe:
    # Initialize Recipe object with list of steps and counter = 0
    def __init__(self, recipeString: str):
        self.steps = self.parseInstrString(recipeString)
        self.stepCounter = 0

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
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------


# 13 steps
test = "Quantity; 1; Prepare two 9-inch pie crusts and one 9-inch pie dish| Measurement; 150; Measure out 150 grams of white sugar| Measurement; 5.69; Measure out 5.69 grams of ground cinnamon| Quantity; 6; Prepare 6 cups of sliced apples| Measurement; 14; Measure out 14 grams of butter| Temperature; 450; Gather the ingredients. Preheat the oven to 450 degrees F (230 degrees C)| Untimed; None; Line your 9-inch pie dish with one pastry crust. Set other one to the side| Untimed; None; Combine 3/4 cup sugar and cinnamon in a small bowl. Add more sugar if your apples are tart| Untimed; None; Layer apple slices in the prepared pie dish, sprinkling each layer with cinnamon-sugar mixture| Untimed; None; Dot top layer with small pieces of butter. Cover with top crust| Timed; 600; Bake pie on the lowest rack of the preheated oven for 10 minutes| Timed; 1800; Reduce oven temperature to 350 degrees F (175 degrees C) and continue baking for about 30 minutes, until golden brown and filling bubbles| Finish; None; Serve!"

recipe = Recipe(test)
print(recipe.getCurrentInstruction())
for x in range(12):
    recipe.incrementStepCounter()
    say(recipe.getCurrentInstruction())

for x in range (12):
    recipe.decrementStepCounter()
    print(recipe.getCurrentInstruction())
