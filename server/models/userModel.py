from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User:
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    def __init__(
            self, id=0, user_mac=None, user_ip=None, first_name="", last_name="", 
            allergies=None, inventory=None, hasScale=False, hasThermometer=False):
        self.id = id
        self.address = {
            "userMAC": user_mac,
            "userIP": user_ip
        }
        self.data = {
            "firstName": first_name,
            "lastName": last_name,
            "allergies": allergies,
            "inventory": inventory
        }
        self.preferences = {
            "hasScale": hasScale,
            "hasThermometer": hasThermometer
        }
    
    def __repr__(self):
        return f"<id={self.id}, User(name={self.first_name} {self.last_name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "address": self.address,
            "data": self.data,
            "preferences": self.preferences
        }