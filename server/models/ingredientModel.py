from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship
import enum
import re
from typing import Tuple

Base = declarative_base()

class MeasureType(enum.Enum):
    WEIGHT = "Weight"  # Weight in grams (converted from other units)
    VOLUME = "Volume" # Volume in ml (converted from other units)
    COUNT = "Count" # Count

measureTypeMapping = {
    # Mapping for weight input
    "mg": [ MeasureType.WEIGHT, 0.001 ],
    "milligram": [ MeasureType.WEIGHT, 0.001 ],
    "g": [ MeasureType.WEIGHT, 1 ],
    "gram": [ MeasureType.WEIGHT, 1 ],
    "kg":[ MeasureType.WEIGHT, 1000 ],
    "kilogram": [ MeasureType.WEIGHT, 1000 ],
    "lb": [ MeasureType.WEIGHT, 453.592 ],
    "pound": [ MeasureType.WEIGHT, 453.592 ],


    # Mapping for volume input
    "ml": [ MeasureType.VOLUME, 1 ],
    "milliliter": [ MeasureType.VOLUME, 1 ],
    "l": [ MeasureType.VOLUME, 1000 ],
    "liter": [ MeasureType.VOLUME, 1000 ],
    "fl oz": [ MeasureType.VOLUME, 29.5735 ],
    "fluid ounce": [ MeasureType.VOLUME, 29.5735 ],
    "cup": [ MeasureType.VOLUME, 236.588 ],
    "cups": [ MeasureType.VOLUME, 236.588 ],
    "tsp": [ MeasureType.VOLUME, 5 ],
    "teaspoon": [ MeasureType.VOLUME, 5 ],
    "tbsp": [ MeasureType.VOLUME, 15 ],
    "tablespoon": [ MeasureType.VOLUME, 15 ],

    # Mapping for count input
    "count": [ MeasureType.COUNT, 1 ],
    "piece": [ MeasureType.COUNT, 1 ],
    "pieces": [ MeasureType.COUNT, 1 ],
    "dozen": [ MeasureType.COUNT, 12 ],
    "dozens": [ MeasureType.COUNT, 12 ],
    "can": [ MeasureType.COUNT, 1 ],
    "cans": [ MeasureType.COUNT, 1 ]

}

def getMeasureType(rawType: str) -> Tuple[ MeasureType, float ]:
    return measureTypeMapping.get( rawType, [ MeasureType.COUNT, 1] )

def standardize(rawName: str) -> str:
    rawName = re.sub(r'[^a-zA-Z\s]', '', rawName).strip()
    return re.sub(r'[\s\_]+', '_', rawName).lower()

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    measureType = Column(Enum(MeasureType), nullable=False)

    recipes = relationship('RecipeIngredient', secondary='recipe_ingredients_association', back_populates='ingredient')
    allergic_users = relationship('User', secondary='user_allergy', back_populates='allergies')

    def __init__(self, name="", measureType=MeasureType.WEIGHT):
        self.name = standardize(name)
        self.measureType = measureType

    def __repr__(self):
        return f"""<id={self.id}, Ingredient(<name={self.name})>"""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class InventoryIngredient(Base):
    __tablename__ = 'inventory_ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    measureType = Column(Enum(MeasureType), nullable=False)

    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='inventory')
    ingredient = relationship('Ingredient')

    def __init__(self, ingredient_id=None, user_id=None, quantity=0, measureType=MeasureType.WEIGHT):
        mType = getMeasureType(measureType)
        self.measureType = mType[0]
        self.quantity = quantity*mType[1]
        self.user_id = user_id
        self.ingredient_id = ingredient_id

    def __repr__(self):
        return f"""<id={self.id}, InventoryIngredient(<user_id={self.user_id}, ingredient_id={self.ingredient_id}, quantity={self.quantity}, measureType={self.measureType})>"""

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ingredient_id": self.ingredient_id,
            "quantity": self.quantity,
            "measureType": self.measureType
        }


class Allergy(Ingredient):
    __tablename__ = 'allergy_ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="allergies")