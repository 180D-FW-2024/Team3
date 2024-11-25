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
print(testRecipeIngredient)

testRecipe.ingredients.append(testRecipeIngredient)

# Add the posts to the session and commit
session.add(testUser)
session.add(testAllergy)
session.add(testInventory)
session.add(testRecipe)
session.commit()

# Query the database to verify the insertion
for user in session.query(User).all():
    print(user)

for allergy in session.query(Allergy).all():
    print(allergy)

for recipe in session.query(Recipe).all():
    print(recipe)