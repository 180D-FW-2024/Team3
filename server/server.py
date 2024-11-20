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

@app.route("/<username>", methods=['GET'])
# Initial call to return userID from source IP 
def start_session(username):
    user = session.query(User).filter_by(username=username).first()
    
    if user is None:
        session.add(User(username=username))
        session.commit()
        user = session.query(User).filter_by(username=username).first()
        return jsonify(user.to_dict()), 201
    
    return jsonify(user.to_dict()), 200

