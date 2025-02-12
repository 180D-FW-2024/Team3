import requests
import random
import string
import dotenv
import os 

dotenv.load_dotenv()
backend_url = os.getenv("BACKEND_URL")

script_dir = os.path.dirname(os.path.abspath(__file__))

def removeUsername(file_path):
    foundLine = False
    with open(file_path, "w") as file:
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
                response = requests.get(backend_url + "/get-user/" + username)
                if response.status_code != 200:
                    removeUsername(real_file_path)
                    return None
                return response.json()["id"]
    return None

def createUser(file_path):
    real_file_path = os.path.join(script_dir, file_path)
    # Open the file in read mode
    with open(real_file_path, 'r') as file:
        for line in file:
            if line.startswith('USERNAME:'):
                return None
    
    # Open the file in append mode
    with open(real_file_path, 'a') as file:
        while True:
            randomString = ''.join(random.choices(string.ascii_letters, k=15))
            response = requests.post(backend_url + "/create-user?username=" + randomString)
            if response.status_code == 201:
                file.write("USERNAME:" + randomString + "\n")
                return response.json()["id"]

def loadUserId(file_path):
    userId = getUserId(file_path)
    if userId is None:
        userId = createUser(file_path)
    return userId