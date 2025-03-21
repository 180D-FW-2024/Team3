from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .ingredientModel import user_allergy_association, Allergy
from .Base import Base
from sqlalchemy.sql import func

user_history_association = Table(
    'user_history', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('recipe_id', ForeignKey('recipes.id'), primary_key=True)
)


class TelegramRegistration(Base):
    __tablename__ = 'telegram_registration'

    user_code = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    generation_time = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, user_code, user_id):
        self.user_code = user_code
        self.user_id = user_id
        # self.generation_time = datetime.utcnow().date()
    
    def __repr__(self):
        return f"""<user_code={self.user_code}, user_id={self.user_id}, generation_time={self.generation_time}>"""

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    username = Column(String, unique=True)
    phone_number = Column(String)#, unique=True)
    allergies = relationship('Allergy', secondary=user_allergy_association, back_populates='users')
    inventory = relationship('InventoryIngredient', back_populates='user', cascade="all, delete-orphan")
    recipe_history = relationship('Recipe', secondary=user_history_association)
    has_scale = Column(Boolean, nullable=False)
    has_thermometer = Column(Boolean, nullable=False)
    telegram_id = Column(String)


    def __init__(
            self, first_name="", username="", phone_number="", hasScale=False, hasThermometer=False, telegram_id=""):
        self.first_name = first_name
        self.username = username
        self.has_scale = hasScale
        self.has_thermometer = hasThermometer
        self.phone_number = phone_number
        self.telegram_id = telegram_id
    
    def __repr__(self):
        return f"""<id={self.id}, User(<first_name={self.first_name}, username={self.username},
                allergies={self.allergies}, inventory={self.inventory},
                has_scale={self.has_scale}, has_thermometer={self.has_thermometer}, telegram_id={self.telegram_id})>"""

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
    
    def addInventory(self, inventoryItem):
        if inventoryItem in self.inventory:
            return False
        self.inventory.append(inventoryItem)
        return True
    
    def removeInventory(self, inventoryItem):
        if inventoryItem not in self.inventory:
            return False
        self.inventory.remove(inventoryItem)
        return True
    
    
    def addRecipeHistory(self, recipe):
        if recipe not in self.recipe_history:
            self.recipe_history.append(recipe)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "username": self.username,
            "allergies": [allergy.name for allergy in self.allergies],
            "inventory": [str(item) for item in self.inventory],
            "hasScale": self.has_scale,
            "phone_number": self.phone_number,
            "hasThermometer": self.has_thermometer
        }