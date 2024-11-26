from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .ingredientModel import user_allergy_association, Allergy
from .Base import Base

user_history_association = Table(
    'user_history', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('recipe_id', ForeignKey('recipes.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    username = Column(String, unique=True)
    allergies = relationship('Allergy', secondary=user_allergy_association, back_populates='users')
    inventory = relationship('InventoryIngredient', back_populates='user')
    recipe_history = relationship('Recipe', secondary=user_history_association)
    has_scale = Column(Integer, nullable=False)
    has_thermometer = Column(Integer, nullable=False)


    def __init__(
            self, first_name="", username="", hasScale=False, hasThermometer=False):
        self.first_name = first_name
        self.username = username
        self.has_scale = hasScale
        self.has_thermometer = hasThermometer
    
    def __repr__(self):
        return f"""<id={self.id}, User(<first_name={self.first_name}, username={self.username},
                allergies={self.allergies}, inventory={self.inventory},
                has_scale={self.has_scale}, has_thermometer={self.has_thermometer})>"""

    def addAllergy(self, allergy):
        if allergy in self.allergies:
            return False
        self.allergies.append(allergy)
        return True
    
    def removeAllergy(self, allergy):
        if allergy not in self.allergies:
            return False
        self.allergies.remove(allergy)
        return True
    
    def addInventory(self, itemName, quantity, measureType):
        pass
    
    def addRecipeHistory(self, recipe):
        if recipe not in self.recipe_history:
            self.recipe_history.append(recipe)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "username": self.username,
            "allergies": self.allergies,
            "inventory": self.inventory,
            "hasScale": self.has_scale,
            "hasThermometer": self.has_thermometer
        }