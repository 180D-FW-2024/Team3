# Flask script for handling incoming requests
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, and_, not_
from sqlalchemy.orm import sessionmaker
from .models.userModel import User
from .models.recipeModel import Recipe
from .models.ingredientModel import Allergy, RecipeIngredient
import subprocess

# Run test_db.py to test database, remove on database completion
subprocess.run(["python3", "test_db.py"])

app = Flask(__name__)

engine = create_engine('sqlite:///raspitouille.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()


@app.route("/<username>", methods=['GET'])
def start_session(username):
    """
    Handles a GET request to /<username>.  If the user exists in the
    database, return the user as a JSON object.  If the user does not
    exist, create a new user with the given username and return the new
    user as a JSON object with a 201 status code.

    Parameters
    ----------
    username : str
        The username of the user to retrieve or create

    Returns
    -------
    JSON object
        The user as a JSON object

    Status Codes
    ------------
    200 : The user already exists in the database
    201 : The user does not exist in the database and was created
    """
    
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        session.add(User(username=username))
        session.commit()
        user = session.query(User).filter_by(username=username).first()
        return jsonify(user.to_dict()), 201
    
    return jsonify(user.to_dict()), 200

@app.route("/add-allergy/<user_id>/<allergy_name>", methods=['PUT'])
def add_allergy(user_id, allergy_name):
    """
    Handles a PUT request to /add-allergy/<user_id>/<allergy_name>.  Adds an
    allergy to a user in the database.  If the user does not exist, return a
    404 error.  If the allergy does not exist, create a new allergy with the
    given name and add it to the user.

    Parameters
    ----------
    user_id : int
        The ID of the user to add an allergy to
    allergy_name : str
        The name of the allergy to add

    Returns
    -------
    JSON object
        The user as a JSON object with the added allergy

    Status Codes
    ------------
    200 : The user exists in the database and the allergy was added
    404 : The user does not exist in the database
    """
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    allergy = session.query(Allergy).filter_by(name=allergy_name).first()
    if allergy is None:
        allergy = Allergy(name=allergy_name)
    user.addAllergy(allergy)
    session.commit()    
    return jsonify(user.to_dict()), 200

@app.route("/remove-allergy/<user_id>/<allergy_name>", methods=['PUT'])
def remove_allergy(user_id, allergy_name):
    """
    Handles a PUT request to /remove-allergy/<user_id>/<allergy_name>.  Removes
    an allergy from a user in the database.  If the user does not exist, return a
    404 error.  If the allergy does not exist, return a 404 error.

    Parameters
    ----------
    user_id : int
        The ID of the user to remove an allergy from
    allergy_name : str
        The name of the allergy to remove

    Returns
    -------
    JSON object
        The user as a JSON object with the removed allergy

    Status Codes
    ------------
    200 : The user exists in the database and the allergy was removed
    404 : The user does not exist in the database
    404 : The allergy does not exist in the database
    """
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

@app.route("/suggest-recipes/<user_id>", methods=['GET'])
def suggest_recipes(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    userAllergyNames = [allergy.name for allergy in user.allergies]
    userInventoryNames = [ingredient.name for ingredient in user.inventory]
    userInventoryMap = {ingredient.name: ingredient.quantity for ingredient in user.inventory}
    validRecipes = session.query(Recipe).filter(
        not_( Recipe.ingredients.any(RecipeIngredient.name.in_(userAllergyNames)) ),
        Recipe.ingredients.all( and_( RecipeIngredient.name.in_(userInventoryNames), 
                                      RecipeIngredient.quantity <= userInventoryMap[RecipeIngredient.name]))
    ).all()
    return jsonify([recipe.to_dict() for recipe in validRecipes]), 200

@app.route("/start-recipe/<recipe_id>/<user_id>", methods=['PUT'])
def start_recipe(recipe_id, user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404
    user.addRecipeHistory(recipe)
    session.commit()
    return jsonify(user.to_dict()), 200

@app.route("/modify-inventory/<user_id>/<ingredient_name>/<quantity>/<measureType>/<changeType>", methods=['PUT'])
def modify_inventory(user_id, ingredient_name, quantity, measureType, changeType):
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    quantity_n = int(quantity) if changeType == "add" else (int(quantity) * -1)
    user.addInventory(itemName=ingredient_name, quantity=quantity_n, measureType=measureType)
    session.commit()
    return jsonify(user.to_dict()), 200
    
