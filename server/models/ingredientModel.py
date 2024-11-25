from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship
from .helpers import MeasureType, standardize, getMeasureType
from .recipeModel import Recipe#, recipe_ingredients_association
from .Base import Base

user_allergy_association = Table(
    'user_allergy', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('allergy_id', ForeignKey('allergies.id'), primary_key=True)
)
'''
class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    measureType = Column(Enum(MeasureType), nullable=False)

    recipes = relationship('Recipe', secondary='recipe_ingredients_association', back_populates='ingredients')

    def __init__(self, name="", measureType=MeasureType.WEIGHT):
        self.name = standardize(name)
        self.measureType = measureType

    def __repr__(self):
        return f"""<id={self.id}, Ingredient(name={self.name}, measureType={self.measureType}, 
            recipes={self.recipes})>"""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "measureType": self.measureType,
            "recipes": [recipe.to_dict() for recipe in self.recipes]
        }
'''
class InventoryIngredient(Base):
    __tablename__ = 'inventory_ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    measureType = Column(Enum(MeasureType), nullable=False)

    #ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='inventory')

    def __init__(self, ingredient_id=None, user_id=None, user=None, quantity=0, measureType=MeasureType.WEIGHT):
        mType = getMeasureType(measureType)
        self.measureType = mType[0]
        self.quantity = quantity*mType[1]
        if user is not None:
            self.user = user
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Either user or user_id must be provided")
        self.ingredient_id = ingredient_id


    def __repr__(self):
        return f"""<id={self.id}, InventoryIngredient(<user_id={self.user_id}, ingredient_id={self.ingredient_id}, quantity={self.quantity}, measureType={self.measureType})>"""

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "ingredientId": self.ingredient_id,
            "quantity": self.quantity,
            "measureType": self.measureType
        }


class Allergy(Base):
    __tablename__ = 'allergies'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    users = relationship("User", secondary=user_allergy_association, back_populates="allergies")
    measureType = Column(Enum(MeasureType), nullable=False)

    def __init__(self, name="", measureType=MeasureType.WEIGHT, user=None):
        self.name = standardize(name)
        self.measureType = measureType
        if user is not None:
            self.addUser(user)

    def addUser(self, user):
        self.users.append(user)

    def __repr__(self):
        return f"""<id={self.id}, Allergy(name={self.name}, name={self.name}, measureType={self.measureType})>"""
