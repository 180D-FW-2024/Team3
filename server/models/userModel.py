from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_mac = Column(String)
    user_ip = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    allergies = Column(String, nullable=False)
    inventory = Column(String, nullable=False)
    hasScale = Column(Integer, nullable=False)
    hasThermometer = Column(Integer, nullable=False)

    def __init__(
            self, id=0, user_mac=None, user_ip=None, first_name="", last_name="", 
            allergies="", inventory="", hasScale=False, hasThermometer=False):
        self.id = id
        self.user_mac = user_mac
        self.user_ip = user_ip
        self.first_name = first_name
        self.last_name = last_name
        self.allergies = allergies
        self.inventory = inventory
        self.hasScale = hasScale
        self.hasThermometer = hasThermometer
    
    def __repr__(self):
        return f"""<id={self.id}, User(<user_mac={self.user_mac}, user_ip={self.user_ip}>,
                first_name={self.first_name}, last_name={self.last_name},
                allergies={self.allergies}, inventory={self.inventory},
                hasScale={self.hasScale}, hasThermometer={self.hasThermometer})>"""

    def to_dict(self):
        return {
            "id": self.id,
            "user_mac": self.user_mac,
            "user_ip": self.user_ip,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "allergies": self.allergies,
            "inventory": self.inventory,
            "hasScale": self.hasScale,
            "hasThermometer": self.hasThermometer
        }