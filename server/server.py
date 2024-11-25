# Flask script for handling incoming requests
from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.userModel import User
from .models.recipeModel import Recipe
from .models.ingredientModel import Allergy
import subprocess

subprocess.run(["python3", "test_db.py"])

app = Flask(__name__)

engine = create_engine('sqlite:///raspitouille.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

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

@app.route("/add-allergy/<user_id>/<allergy_name>", methods=['POST'])
def add_allergy(user_id, allergy_name):
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    allergy = session.query(Allergy).filter_by(name=allergy_name).first()
    if allergy is None:
        allergy = Allergy(name=allergy_name)
    user.addAllergy(allergy)
    session.commit()
    return jsonify(user.to_dict()), 200

@app.route("/remove-allergy/<user_id>/<allergy_name>", methods=['POST'])
def remove_allergy(user_id, allergy_name):
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    allergy = session.query(Allergy).filter_by(name=allergy_name).first()
    if allergy is None:
        return jsonify({"error": "Allergy not found"}), 404
    user.removeAllergy(allergy)
    session.commit()
    return jsonify(user.to_dict()), 200

@app.route("/get-allergies/<user_id>", methods=['GET'])
def get_allergies(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@app.route("/get-recipe/<recipe_id>", methods=['GET'])
def get_recipe(recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    return jsonify(recipe.to_dict()), 200
