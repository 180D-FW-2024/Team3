from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.userModel import User, Base  # Import the User model and Base from models.py
from models.ingredientModel import Allergy, user_allergy_association#, recipe_ingredients_association
from models.helpers import MeasureType

# Set up the database engine and session
engine = create_engine('sqlite:///Users.db', echo=True)
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
    name="testAllergy",
    measureType=MeasureType.WEIGHT,
    user=testUser
)
print(testAllergy)

# Add the posts to the session and commit
session.add(testUser)
#session.add(testAllergy)
session.commit()

# Query the database to verify the insertion
for user in session.query(User).all():
    print(user)