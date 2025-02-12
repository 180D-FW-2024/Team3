# from scale_reader import get_weight_in_grams
# from thermometer_reader import get_current_temperature_f

# # print(get_current_temperature_f())
# # print(get_weight_in_grams())

from recipe_handler import CountdownTimer
import time
import speech_recognition as sr
from text_to_speech import tts as say
from command_handler import handle_command, addIngredientHandler, addIngredientCamHandler, removeIngredientHandler, recommendRecipeHandler, addAllergyHandler, removeAllergyHandler
from recipe_handler import Recipe
from userSetup import loadUserId
from LLM.LLMAgent import send_command, options
from image_recognition.image_recognition import IngredientRecog
import dotenv
import requests
import os
import re
import sounddevice
import random
import string

say("success")
# timer = CountdownTimer(5)
# timer.start()
# time.sleep(2)
# print(timer.time_left())