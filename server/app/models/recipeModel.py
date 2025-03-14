from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .helpers import InstructionType
from .Base import Base
import re

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    completion_time = Column(Integer, nullable=False)
    ingredients = relationship('RecipeIngredient', back_populates='recipe')
    recipe_text = Column(String, nullable=False)
    scale_needed = Column(Boolean, nullable=False)
    thermometer_needed = Column(Boolean, nullable=False)


    def __init__(self, title="", recipe_text="", scale_needed=False, thermometer_needed=False, completion_time=0):
        self.recipe_text = re.sub(r'\n+', '', recipe_text)
        self.title = title
        self.scale_needed = scale_needed
        self.thermometer_needed = thermometer_needed
        self.completion_time = completion_time
    
    def __repr__(self):
        ingredients = ", ".join([ingredient.name for ingredient in self.ingredients])
        return f"<id={self.id}, Recipe(title={self.title}, completion_time={self.completion_time}, recipe_text={self.recipe_text}, ingredients={ingredients}, scale_needed={self.scale_needed}, thermometer_needed={self.thermometer_needed})"

    def addIngredient(self, ingredient):
        self.ingredients.append(ingredient)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe_text': self.recipe_text,
            'completion_time': self.completion_time,
            'ingredients': [ingredient.to_dict() for ingredient in self.ingredients],
            'scale_needed': self.scale_needed,
            'thermometer_needed': self.thermometer_needed,
            'completion_time': self.completion_time
        }
