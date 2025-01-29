from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.userModel import User, TelegramRegistration, Base  # Import the User model and Base from models.py
from models.ingredientModel import Allergy, RecipeIngredient, InventoryIngredient, user_allergy_association
from models.recipeModel import Recipe
from models.helpers import MeasureType

# Set up the database engine and session
engine = create_engine('sqlite:///raspitouille.db')#, echo=True)
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