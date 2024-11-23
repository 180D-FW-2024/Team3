from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship
from models.helpers import MeasureType, standardize, getMeasureType

Base = declarative_base()

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
            "userId": self.user_id,
            "ingredientId": self.ingredient_id,
            "quantity": self.quantity,
            "measureType": self.measureType
        }


class Allergy(Ingredient):
    __tablename__ = 'allergy_ingredients'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="allergies")