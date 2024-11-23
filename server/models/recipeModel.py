from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from models.helpers import InstructionType

Base = declarative_base()

recipe_ingredients_association = Table(
    'recipe_ingredients_association', Base.metadata,
    Column('recipe_id', ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', ForeignKey('ingredients.id'), primary_key=True)
)

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    ingredients = relationship('RecipeIngredient', secondary='recipe_ingredients_association', back_populates='recipes')
    recipe_text = Column(String, nullable=False)
    scale_needed = Column(Integer, nullable=False)
    thermometer_needed = Column(Integer, nullable=False)


    def __init__(self, title="", recipe_text="", scale_needed=False, thermometer_needed=False):
        self.recipe_text = recipe_text
        self.title = title
        self.scale_needed = scale_needed
        self.thermometer_needed = thermometer_needed

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe_text': self.recipe_text,
            'ingredients': [ingredient.to_dict() for ingredient in self.ingredients],
            'scale_needed': self.scale_needed,
            'thermometer_needed': self.thermometer_needed
        }
