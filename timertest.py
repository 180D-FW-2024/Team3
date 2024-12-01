from recipe_handler import Recipe
import time

test = "Quantity; 1; Prepare two 9-inch pie crusts and one 9-inch pie dish| Measurement; 150; Measure out 150 grams of white sugar| Measurement; 5.69; Measure out 5.69 grams of ground cinnamon| Quantity; 6; Prepare 6 cups of sliced apples| Measurement; 14; Measure out 14 grams of butter| Temperature; 450; Gather the ingredients. Preheat the oven to 450 degrees F (230 degrees C)| Untimed; None; Line your 9-inch pie dish with one pastry crust. Set other one to the side| Untimed; None; Combine 3/4 cup sugar and cinnamon in a small bowl. Add more sugar if your apples are tart| Untimed; None; Layer apple slices in the prepared pie dish, sprinkling each layer with cinnamon-sugar mixture| Untimed; None; Dot top layer with small pieces of butter. Cover with top crust| Timed; 600; Bake pie on the lowest rack of the preheated oven for 10 minutes| Timed; 1800; Reduce oven temperature to 350 degrees F (175 degrees C) and continue baking for about 30 minutes, until golden brown and filling bubbles| Finish; None; Serve!"
recipe = Recipe(test)
for x in range(10):
    recipe.incrementStepCounter()

recipe.currentStep()
recipe.timeRemaning()

recipe.nextStep()

# TESTS

# 13 steps
# test = "Quantity; 1; Prepare two 9-inch pie crusts and one 9-inch pie dish| Measurement; 150; Measure out 150 grams of white sugar| Measurement; 5.69; Measure out 5.69 grams of ground cinnamon| Quantity; 6; Prepare 6 cups of sliced apples| Measurement; 14; Measure out 14 grams of butter| Temperature; 450; Gather the ingredients. Preheat the oven to 450 degrees F (230 degrees C)| Untimed; None; Line your 9-inch pie dish with one pastry crust. Set other one to the side| Untimed; None; Combine 3/4 cup sugar and cinnamon in a small bowl. Add more sugar if your apples are tart| Untimed; None; Layer apple slices in the prepared pie dish, sprinkling each layer with cinnamon-sugar mixture| Untimed; None; Dot top layer with small pieces of butter. Cover with top crust| Timed; 600; Bake pie on the lowest rack of the preheated oven for 10 minutes| Timed; 1800; Reduce oven temperature to 350 degrees F (175 degrees C) and continue baking for about 30 minutes, until golden brown and filling bubbles| Finish; None; Serve!"

# recipe = Recipe(test)
# jump to 10 min pie bake step
# for x in range(10):
#     recipe.incrementStepCounter()
# recipe.currentStep()
# recipe.nextStep()


# print(recipe.timer.initial_duration)
# recipe.timer.start()
# time.sleep(5)
# print(recipe.timer.time_left())
# recipe.timer.pause()
# time.sleep(3)
# print(recipe.timer.time_left())