from flask import Flask
import subprocess

subprocess.run(["bash", "FlaskExports.sh"])
subprocess.run(["python3", "init_db.py"])

app = Flask(__name__)

# Import your routes and models here
from app import server