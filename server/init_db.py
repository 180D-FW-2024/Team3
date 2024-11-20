from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.userModel import User, Base  # Import the User model and Base from models.py

# Set up the database engine and session
engine = create_engine('sqlite:///Users.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Ensure the table is created (if it doesn't already exist)
Base.metadata.drop_all(engine, tables=[User.__table__])
Base.metadata.create_all(engine, tables=[User.__table__])

# Create and insert new posts
testUser = User(
    first_name="Test",
    username="testuser",
    allergies="",
    inventory="",
    hasScale=False,
    hasThermometer=False
)
print(testUser)


# Add the posts to the session and commit
session.add(testUser)
session.commit()

# Query the database to verify the insertion
for user in session.query(User).all():
    print(user)