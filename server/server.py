# Flask script for handling incoming requests
from flask import Flask

app = Flask(__name__)

@app.route("/")
# Initial call to return userID from source IP 
def start_session():
    return 