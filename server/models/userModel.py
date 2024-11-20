from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    allergies = Column(String, nullable=False)
    inventory = Column(String, nullable=False)
    hasScale = Column(Integer, nullable=False)
    hasThermometer = Column(Integer, nullable=False)

    def __init__(
            self, id=0, first_name="", username="", 
            allergies="", inventory="", hasScale=False, hasThermometer=False):
        self.id = id
        self.first_name = first_name
        self.username = username
        self.allergies = allergies
        self.inventory = inventory
        self.hasScale = hasScale
        self.hasThermometer = hasThermometer
    
    def __repr__(self):
        return f"""<id={self.id}, User(<first_name={self.first_name}, username={self.username},
                allergies={self.allergies}, inventory={self.inventory},
                hasScale={self.hasScale}, hasThermometer={self.hasThermometer})>"""

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "username": self.username,
            "allergies": self.allergies,
            "inventory": self.inventory,
            "hasScale": self.hasScale,
            "hasThermometer": self.hasThermometer
        }