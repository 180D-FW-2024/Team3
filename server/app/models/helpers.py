import enum
import re
from typing import Tuple

class MeasureType(enum.Enum):
    WEIGHT = "Weight"  # Weight in grams (converted from other units)
    VOLUME = "Volume" # Volume in ml (converted from other units)
    COUNT = "Count" # Count

    def __str__(self):
        return self.value

class InstructionType(enum.Enum):
    TIMED = "Timed"
    UNTIMED = "Untimed"
    TEMPERATURE = "Temperature"
    MEASUREMENT = "Measurement"
    QUANTITY = "Quantity"
    FINISH = "Finish"


measureTypeMapping = {
    # Mapping for weight input
    "mg": [ MeasureType.WEIGHT, 0.001 ],
    "milligram": [ MeasureType.WEIGHT, 0.001 ],
    "milligrams": [ MeasureType.WEIGHT, 0.001 ],
    "g": [ MeasureType.WEIGHT, 1 ],
    "gram": [ MeasureType.WEIGHT, 1 ],  
    "grams": [ MeasureType.WEIGHT, 1 ],
    "kg":[ MeasureType.WEIGHT, 1000 ],
    "kilogram": [ MeasureType.WEIGHT, 1000 ],
    "kilograms": [ MeasureType.WEIGHT, 1000 ],
    "lb": [ MeasureType.WEIGHT, 453.592 ],
    "lbs": [ MeasureType.WEIGHT, 453.592 ],
    "pound": [ MeasureType.WEIGHT, 453.592 ],
    "pounds": [ MeasureType.WEIGHT, 453.592 ],


    # Mapping for volume input
    "ml": [ MeasureType.VOLUME, 1 ],
    "milliliter": [ MeasureType.VOLUME, 1 ],
    "milliliters": [ MeasureType.VOLUME, 1 ],
    "l": [ MeasureType.VOLUME, 1000 ],
    "liter": [ MeasureType.VOLUME, 1000 ],
    "liters": [ MeasureType.VOLUME, 1000 ],
    "fl oz": [ MeasureType.VOLUME, 29.5735 ],
    "fluid ounce": [ MeasureType.VOLUME, 29.5735 ],
    "fluid ounces": [ MeasureType.VOLUME, 29.5735 ],
    "cup": [ MeasureType.VOLUME, 236.588 ],
    "cups": [ MeasureType.VOLUME, 236.588 ],
    "tsp": [ MeasureType.VOLUME, 5 ],
    "teaspoon": [ MeasureType.VOLUME, 5 ],
    "teaspoons": [ MeasureType.VOLUME, 5 ],
    "tbsp": [ MeasureType.VOLUME, 15 ],
    "tablespoon": [ MeasureType.VOLUME, 15 ],
    "tablespoons": [ MeasureType.VOLUME, 15 ],
    "quart": [ MeasureType.VOLUME, 946],
    "quarts": [ MeasureType.VOLUME, 946],

    # Mapping for count input
    "count": [ MeasureType.COUNT, 1 ],
    "piece": [ MeasureType.COUNT, 1 ],
    "pieces": [ MeasureType.COUNT, 1 ],
    "dozen": [ MeasureType.COUNT, 12 ],
    "dozens": [ MeasureType.COUNT, 12 ],
    "can": [ MeasureType.COUNT, 1 ],
    "cans": [ MeasureType.COUNT, 1 ]

}

def getMeasureType(rawType: str) -> Tuple[ MeasureType, float ]:
    return measureTypeMapping.get( rawType, [ MeasureType.COUNT, 1] )

def standardize(rawName: str) -> str:
    if rawName is None:
        return None
    rawName = re.sub(r'[^a-zA-Z\s0-9]', '', rawName).strip()
    return re.sub(r'[\s\_]+', '_', rawName).lower()