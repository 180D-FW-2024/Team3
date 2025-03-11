import requests
import random
import string
import dotenv
import os 
from text_to_speech import tts as say
from image_recognition.image_recognition import IngredientRecog

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

script_dir = os.path.dirname(os.path.abspath(__file__))

def removeUsername(file_path):
    foundLine = False
    with open(file_path, "r+") as file:
        for line in file:
            if "USERNAME" not in line:
                file.write(line)
            else:
                foundLine = True
    return foundLine

def getUserId(file_path):
    real_file_path = os.path.join(script_dir, file_path)
    # Open the file in read mode
    username = None
    with open(real_file_path, 'r') as file:
        if file is None:
            return None
        # Read the content of the file line by line
        for line in file:
            # Check if the line contains the string 'USERNAME:'
            if line.startswith('USERNAME:'):
                # Extract and return the part after 'USERNAME:'
                username = line.split(':', 1)[1].strip()  # Strip any extra spaces/newlines
                while True:
                    try:
                        print("Retrying...")
                        response = requests.get(backend_url + "/get-user/" + username, timeout=2)
                        if 200 <= response.status_code < 300:  # Check if response is successful
                            break
                        if response.status_code == 404:
                            removeUsername(real_file_path)
                            return None
                    except requests.exceptions.RequestException:  # Catches timeout and other request errors
                        pass  
                return response.json()["id"]
    return None

def createUser(file_path):
    real_file_path = os.path.join(script_dir, file_path)
    with open(real_file_path, 'r') as file:
        for line in file:
            if line.startswith('USERNAME:'):
                return line[len('USERNAME:'):].strip()
    
    image_recognizer = IngredientRecog()

    say("No user logged in. Please go to Raspitouille dot x y z, as shown in our user manual, to login with your phone number.")
    say("Hold the QR in view of my camera.")
    qr_return_val = image_recognizer.scan_qr_login()
    if (not qr_return_val) or qr_return_val[0] == 0:
        say("Phone number added successfully")
    else:
        print(qr_return_val)
        say("Phone number addition failure. Try again.")
        return None
    '''
    real_file_path = os.path.join(script_dir, file_path)
    # Open the file in read mode
    
    # Open the file in append mode
    with open(real_file_path, 'a') as file:
        while True:
            try:
                print("Retrying...")
                response = requests.get(backend_url + "/get-user?username=" + qr_return_val[1], timeout=2)  
                if 200 <= response.status_code < 300:  # Check if response is successful
                    break
                else:
                    return None
            except requests.exceptions.RequestException:  # Catches timeout and other request errors
                pass  
    '''
    return qr_return_val[1]

def loadUserId(file_path):
    userId = getUserId(file_path)
    while (userId is None):
        userId = createUser(file_path)
    return userId