import requests
import random
import string
import dotenv
import os 

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

def getUsername(file_path):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read the content of the file line by line
        for line in file:
            # Check if the line contains the string 'USERNAME:'
            if line.startswith('USERNAME:'):
                # Extract and return the part after 'USERNAME:'
                return line.split(':', 1)[1].strip()  # Strip any extra spaces/newlines
    return None

def createUser(file_path):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('USERNAME:'):
                return None
    
    with open(file_path, 'a') as file:
        while True:
            randomString = ''.join(random.choices(string.ascii_letters, k=15))
            if requests.post(backend_url + "/create-user/" + randomString).status_code == 200:
                file.write("USERNAME:" + randomString + "\n")
                return randomString

def loadUserId(username):
    response = requests.get(backend_url + "/get-user/" + username)
    if response.status_code != 200:
        return None
    return response.json()["id"]