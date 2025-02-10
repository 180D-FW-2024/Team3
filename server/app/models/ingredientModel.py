from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship
from .helpers import MeasureType, standardize, getMeasureType
from .recipeModel import Recipe
from .Base import Base

user_allergy_association = Table(
    'user_allergy', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('allergy_id', ForeignKey('allergies.id'), primary_key=True)
)

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    measureType = Column(Enum(MeasureType), nullable=False)
    quantity = Column(Integer, nullable=False)

    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    recipe = relationship('Recipe', back_populates='ingredients')

    def __init__(self, name="", measureType=MeasureType.WEIGHT, quantity=0):
        self.name = standardize(name)
        self.measureType = measureType
        self.quantity = quantity

    def __repr__(self):
        return f"""<id={self.id}, RecipeIngredient(name={self.name}, quantity={self.quantity}, measureType={self.measureType}, 
            recipe={self.recipe.title})>"""

    def __str__(self):
        if self.measureType == MeasureType.WEIGHT:
            return f"""{self.name}, {self.quantity}_grams"""
        elif self.measureType == MeasureType.VOLUME:
            return f"""{self.name}, {self.quantity}_ml"""
        elif self.measureType == MeasureType.COUNT:
            if self.quantity == 1:
                return f"""{self.quantity} {self.name}"""
            else:
                return f"""{self.quantity} {self.name}s"""
            
        return f"""{self.name}, {self.quantity}_{self.measureType}"""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "measureType": str(self.measureType),
            "quantity": self.quantity
        }

class InventoryIngredient(Base):
    __tablename__ = 'inventory_ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    measureType = Column(Enum(MeasureType), nullable=False)
    name = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='inventory')

    def __init__(self, user_id=None, user=None, name="", quantity=0, measureType=MeasureType.COUNT):
        self.measureType = measureType
        self.quantity = quantity
        if user is not None:
            self.user = user
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Either user or user_id must be provided")
        self.name = standardize(name)


    def __repr__(self):
        return f"""<id={self.id}, InventoryIngredient(<user_id={self.user_id}, name={self.name}, quantity={self.quantity}, measureType={self.measureType})>"""
    
    def __str__(self):
        if self.measureType == MeasureType.WEIGHT:
            return f"""{self.name}, {self.quantity}_grams"""
        elif self.measureType == MeasureType.VOLUME:
            return f"""{self.name}, {self.quantity}_ml"""
        elif self.measureType == MeasureType.COUNT:
            if self.quantity == 1:
                return f"""{self.quantity} {self.name}"""
            else:
                return f"""{self.quantity} {self.name}s"""
            
        return f"""{self.name}, {self.quantity}_{self.measureType}"""

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "ingredientName": self.name,
            "quantity": self.quantity,
            "measureType": self.measureType.__str__(),
            "text": str(self)
        }


class Allergy(Base):
    __tablename__ = 'allergies'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    users = relationship("User", secondary=user_allergy_association, back_populates="allergies")

    def __init__(self, name="", user=None):
        self.name = standardize(name)
        if user is not None:
            self.addUser(user)

    def __repr__(self):
        user_names = {user.username for user in self.users}
        return f"""<id={self.id}, Allergy(name={self.name}, users={user_names})>"""
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "userCount": len(self.users)
        }
