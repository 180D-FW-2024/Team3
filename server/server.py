# Flask script for handling incoming requests
from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.userModel import User
import subprocess

subprocess.run(["bash", "FlaskExports.sh"])
subprocess.run(["python3", "init_db.py"])

app = Flask(__name__)

engine = create_engine('sqlite:///Users.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

from together import Together

client = Together()

response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    messages=[{
        "role": "user",
        "content": """You are a cooking assistant, who will take in user commands as text and respond with the number it corresponds to.\n
         Here is the list of possible commands, each command MUST map to one of these:\n
         1 = Next Instruction, 
         2 = Previous Instruction
         3 = Repeat Instruction
         4 = List Ingredients
         5 = Current Temperature
         6 = Time Remaining
         7 = Start Timer
         8 = Stop Timer
         9 = Add Ingredient
         10 = Remove Ingredient
         Respond with the number that each of the following commands corresponds to."""
    }
    ],
    max_tokens=512,
    temperature=0.7,
    top_p=0.7,
    top_k=50,
    repetition_penalty=1,
    stop=["<|eot_id|>","<|eom_id|>"],
    stream=True
)
assert response is not None
for token in response:
    print(token.choices[0].delta.content, end='', flush=True)

@app.route("/<username>", methods=['GET'])
# Initial call to return userID from source IP, and create if not present
def start_session(username):
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        session.add(User(username=username))
        session.commit()
        user = session.query(User).filter_by(username=username).first()
        return jsonify(user.to_dict()), 201

    return jsonify(user.to_dict()), 200

@app.route("/command/<command>", methods=['GET'])
def map_command(command):
    res = client.send(command)
    res = client.response(res)
    

    return jsonify(res), 200

