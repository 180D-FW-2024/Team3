from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.userModel import User, TelegramRegistration, Base  # Import the User model and Base from models.py
from models.ingredientModel import Allergy, RecipeIngredient, InventoryIngredient, user_allergy_association
from models.recipeModel import Recipe
from models.helpers import MeasureType
import os
import json

def loadRecipe(session, data):
    if data is None or session is None:
        return None
    if (data.get("completion_time") is None or data.get("title") is None or data.get("ingredients") is None 
        or data.get("recipe_text") is None or data.get("scale_needed") is None or data.get("thermometer_needed") is None):
        return None
    newRecipe = Recipe(
        title=data.get("title"),
        recipe_text=data.get("recipe_text"),
        completion_time=data.get("completion_time"),
        scale_needed=data.get("scale_needed"),
        thermometer_needed=data.get("thermometer_needed")
    )
    for ingredient in data.get("ingredients"):
        if ingredient.get("name") is None or ingredient.get("measureType") is None or ingredient.get("quantity") is None:
            continue
        measureType = MeasureType(ingredient.get("measureType"))
        newRecipe.ingredients.append( RecipeIngredient(
            name=ingredient.get("name"),
            measureType=measureType,
            quantity=ingredient.get("quantity")
        ))
    session.add(newRecipe)
    session.commit
    

def databaseLoad(session, recipePath):
    print("recipe path: ", recipePath)
    # directory = os.fsencode(recipePath)
    for file in os.listdir(recipePath):
        filename = os.fsdecode(file)
        print("file:", filename, "dir:", recipePath)
        if filename.endswith(".json"):
            print("loading: ", os.path.join(recipePath, filename))
            with open(os.path.join(recipePath, filename)) as json_file:
                loadRecipe(session, data = json.load(json_file))


# Set up the database engine and session
engine = create_engine('sqlite:///raspitouille.db')#, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

tables = Base.metadata.tables

# Ensure the table is created (if it doesn't already exist)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

databaseLoad(session, "../recipes")

# Create and insert new posts
testUser = User(
    first_name="Test",
    username="testuser",
    hasScale=False,
    hasThermometer=False,
    phone_number="1234567890"
)
print(testUser)

anotherUser = User(
    first_name="Test2",
    username="testuser2",
    hasScale=False,
    hasThermometer=False
)

testAllergy = Allergy(
    name="testAllergy"
)
print(testAllergy)

testUser.addAllergy(testAllergy)

testInventory = InventoryIngredient(
    user=testUser,
    quantity=100,
    measureType=MeasureType.WEIGHT,
    name="sugar"
)
print(testInventory)

testInventoryApple = InventoryIngredient(
    user=testUser,
    quantity=200,
    measureType=MeasureType.COUNT,
    name="apple"
)

testInventory2 = InventoryIngredient(
    user=anotherUser,
    quantity=100,
    measureType=MeasureType.WEIGHT,
    name="salt"
)

testRecipeText = """Quantity; 3; Cut up 3 apples| 
Measurement; 50; Measure out 50 grams of white sugar| 
Untimed; None; Mash apples and mix in sugar in bowl| 
Temperature; 200; Gather the ingredients. Preheat the oven to 200 degrees F| 
Timed; 1200; Place mix in oven in ceramic dish and bake for 20 minutes| 
Finish; None; Serve!"""


testRecipe = Recipe(
    title="Apple Custard",
    recipe_text=testRecipeText,
    completion_time=30,
    scale_needed=False,
    thermometer_needed=False
)
print(testRecipe)

testRecipe2 = Recipe(
    title="Blueberry Pie",
    recipe_text="This is an blueberry pie recipe",
    completion_time=60,
    scale_needed=False,
    thermometer_needed=False
)
print(testRecipe2)

blueberryIngredient = RecipeIngredient(
    name="blueberry",
    measureType=MeasureType.COUNT,
    quantity=40
)

doughIngredient = RecipeIngredient(
    name="flour",
    measureType=MeasureType.WEIGHT,
    quantity=400
)


testRecipe2.ingredients.append(blueberryIngredient)
testRecipe2.ingredients.append(doughIngredient)

testRecipeIngredient = RecipeIngredient(
    name="sugar",
    measureType=MeasureType.WEIGHT,
    quantity=100
)
testRecipeIngredient2 = RecipeIngredient(
    name="apple",
    measureType=MeasureType.COUNT,
    quantity=3
)
print(testRecipeIngredient)

testRecipe.ingredients.append(testRecipeIngredient)
testRecipe.ingredients.append(testRecipeIngredient2)

session.add(testUser)
session.add(anotherUser)
session.add(testAllergy)
session.add(testInventory)
session.add(testInventory2)
session.add(testRecipe)
session.add(testRecipe2)
session.commit()

# Query the database to verify the insertion
for user in session.query(User).all():
    print(user)

for allergy in session.query(Allergy).all():
    print(allergy)

for recipe in session.query(Recipe).all():
    print(recipe)