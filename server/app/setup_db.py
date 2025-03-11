from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.userModel import User, TelegramRegistration, Base  # Import the User model and Base from models.py
from models.ingredientModel import Allergy, RecipeIngredient, InventoryIngredient, user_allergy_association
from models.recipeModel import Recipe
from models.helpers import MeasureType
import os
import dotenv
import json

dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def loadRecipe(session, data):
    if data is None or session is None:
        return None
    if (data.get("completion_time") is None or data.get("title") is None or data.get("ingredients") is None 
        or data.get("recipe_text") is None or data.get("scale_needed") is None or data.get("thermometer_needed") is None):
        return None
    if session.query(Recipe).filter_by(recipe_text=data.get("recipe_text"), title=data.get("title")).first() is not None:
        return
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
        newIngredient = RecipeIngredient(
            name=ingredient.get("name").lower(),
            measureType=measureType,
            quantity=ingredient.get("quantity")
        )
        session.add(newIngredient)
        newRecipe.ingredients.append(newIngredient)
    
    session.add(newRecipe)
    session.commit()
    

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
engine = create_engine(DATABASE_URL)#, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

tables = Base.metadata.tables

# Ensure the table is created (if it doesn't already exist)
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

databaseLoad(session, "./recipes")

# Query the database to verify the insertion
for user in session.query(User).all():
    print(user)

for allergy in session.query(Allergy).all():
    print(allergy)

for recipe in session.query(Recipe).all():
    print("recipe")
    print(recipe)