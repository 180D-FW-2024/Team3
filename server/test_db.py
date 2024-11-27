from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.userModel import User, Base  # Import the User model and Base from models.py
from models.ingredientModel import Allergy, RecipeIngredient, InventoryIngredient, user_allergy_association, recipe_ingredients_association
from models.recipeModel import Recipe
from models.helpers import MeasureType

# Set up the database engine and session
engine = create_engine('sqlite:///raspitouille.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

tables = Base.metadata.tables

# Ensure the table is created (if it doesn't already exist)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Create and insert new posts
testUser = User(
    first_name="Test",
    username="testuser",
    hasScale=False,
    hasThermometer=False
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

testInventory2 = InventoryIngredient(
    user=anotherUser,
    quantity=100,
    measureType=MeasureType.WEIGHT,
    name="salt"
)

testRecipe = Recipe(
    title="Test Recipe",
    recipe_text="This is a test recipe",
    scale_needed=False,
    thermometer_needed=False
)
print(testRecipe)

testRecipeIngredient = RecipeIngredient(
    name="sugar",
    measureType=MeasureType.WEIGHT,
    quantity=100
)
testRecipeIngredient2 = RecipeIngredient(
    name="apples",
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
session.commit()

# Query the database to verify the insertion
for user in session.query(User).all():
    print(user)

for allergy in session.query(Allergy).all():
    print(allergy)

for recipe in session.query(Recipe).all():
    print(recipe)