# Flask script for handling incoming requests
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, not_, func, or_, and_, exists
from sqlalchemy.orm import sessionmaker, aliased
from .models.userModel import User
from .models.recipeModel import Recipe
from .models.ingredientModel import Allergy, RecipeIngredient, InventoryIngredient
from .models.helpers import MeasureType, standardize
from .LLMAgent import send_command, options
import subprocess
import re

# Run test_db.py to test database, remove on database completion
subprocess.run(["python3", "test_db.py"])

app = Flask(__name__)

engine = create_engine('sqlite:///raspitouille.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

@app.route("/command/<command>", methods=['GET'])
def map_command(command):
    output = send_command(re.sub(r'[\_\s\-]+', ' ', command.strip()))
    if output is None:
        return jsonify({ "response": "No API Response" }), 500
    outputString = " ".join([re.sub(r'[\W_]+', '', token) for token in output]).strip().lower()
    if outputString not in options:
        return jsonify({ "response": "Command Not Recognized" }), 400
    else:
        return jsonify({ "response": outputString }), 200

@app.route("/create-user/<username>", methods=['POST'])
def create_user(username):
    """
    Handles a POST request to /create-user/<username>.  Creates a new user in
    the database with the given username.  If the user already exists, returns a
    400 error with a JSON object containing the error message "User already
    exists".  Otherwise, returns the newly created user as a JSON object with a
    201 status code.

    Parameters
    ----------
    username : str
        The username of the new user to create

    Returns
    -------
    JSON object
        The new user as a JSON object, or an error message if the user already
        exists

    Status Codes
    ------------
    201 : The user was successfully created
    400 : The user already exists in the database
    """
    username = standardize(username)
    if session.query(User).filter_by(username=username).first() is not None:
        return jsonify({"error": "User already exists"}), 400
    firstName = request.args.get('firstName')
    session.add(User(username=username, first_name=(firstName if firstName is not None else "")))
    session.commit()
    return jsonify(session.query(User).filter_by(username=username).first().to_dict()), 201

@app.route("/get-user/<username>", methods=['GET'])
def get_user(username):
    """
    Handles a GET request to /<username>.  Returns the user with the given
    username as a JSON object.  If the user does not exist, returns a 404 error
    with a JSON object containing the error message "User not found".

    Parameters
    ----------
    username : str
        The username of the user to retrieve

    Returns
    -------
    JSON object
        The user as a JSON object, or an error message if the user does not
        exist

    Status Codes
    ------------
    200 : The user exists in the database
    404 : The user does not exist in the database
    """
    username = standardize(username)
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
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
    userInventoryMap = {} 
    for ingredient in user.inventory:
        userInventoryMap[ingredient.name] = ingredient.quantity
    print(userInventoryMap)
    userInventoryAlias = aliased(InventoryIngredient)
    validRecipes = (
        session.query(Recipe, RecipeIngredient)
        .outerjoin(RecipeIngredient, RecipeIngredient.recipe_id == Recipe.id)
        .outerjoin(
            InventoryIngredient,
            (RecipeIngredient.name == InventoryIngredient.name) & (InventoryIngredient.user_id == user.id),
        )
        .filter(
            not_(
                Recipe.ingredients.any(RecipeIngredient.name.in_(userAllergyNames))
            )
        )
        .filter(
            not_(
                Recipe.ingredients.any( 
                    InventoryIngredient.name.is_(None) 
                )
            )
        ).all()
    )
    print('Allergy + Missing Filter Results:' + str(validRecipes))

    validRecipes = (
        session.query(Recipe)
        .outerjoin(RecipeIngredient, RecipeIngredient.recipe_id == Recipe.id)
        .outerjoin(
            InventoryIngredient,
            and_((RecipeIngredient.name == InventoryIngredient.name), (InventoryIngredient.user_id == user.id)),
        )
        .filter(
            not_(
                Recipe.ingredients.any(RecipeIngredient.name.in_(userAllergyNames))
            )
        )
        .group_by(Recipe)
        .having(
            func.count(InventoryIngredient.name) == func.count(RecipeIngredient.name)
        )
        .having(
            func.min(InventoryIngredient.quantity - RecipeIngredient.quantity) >= 0
        )
        .all()
    )

    print('Filter results:' + str(validRecipes))

    query = (session.query(Recipe, RecipeIngredient, InventoryIngredient)
    .outerjoin(RecipeIngredient, RecipeIngredient.recipe_id == Recipe.id)
    .outerjoin(
        InventoryIngredient,
        and_((RecipeIngredient.name == InventoryIngredient.name), (InventoryIngredient.user_id == user.id))
    )
    .filter(
        not_(
            Recipe.ingredients.any(RecipeIngredient.name.in_(userAllergyNames))
        )
    )
    )
    

    # Print out the results to see what's happening
    print('full rows' + str(query.all()))
    
    return jsonify([recipe.to_dict() for recipe in validRecipes]), 200

@app.route("/start-recipe/<recipe_id>/<user_id>", methods=['PUT'])
def start_recipe(recipe_id, user_id):
    """
    Handles a PUT request to /start-recipe/<recipe_id>/<user_id>.  Adds a recipe
    to a user's history in the database.  If the user does not exist, return a
    404 error.  If the recipe does not exist, return a 404 error.

    Parameters
    ----------
    recipe_id : int
        The ID of the recipe to add to the user's history
    user_id : int
        The ID of the user to add the recipe to

    Returns
    -------
    JSON object
        The user as a JSON object with the added recipe

    Status Codes
    ------------
    200 : The user exists in the database and the recipe was added
    404 : The user does not exist in the database
    404 : The recipe does not exist in the database
    """
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404
    user.addRecipeHistory(recipe)
    session.commit()
    return jsonify(user.to_dict()), 200

@app.route("/modify-inventory/<user_id>/<ingredient_name>/<quantity>/<measureTypeName>/<changeType>", methods=['PUT'])
def modify_inventory(user_id, ingredient_name, quantity, measureTypeName, changeType):
    try:
        measureType = MeasureType(measureTypeName.capitalize())
    except ValueError:
        return jsonify({"error": "Invalid measure type"}), 400
    
    user = session.query(User).filter_by(id=user_id).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404
    try:
        quantity_n = int(quantity) if changeType == "add" else (int(quantity) * -1)
    except ValueError:
        return jsonify({"error": "Invalid quantity"}), 400
    
    inventoryItem = session.query(InventoryIngredient).filter_by(user_id=user_id, name=ingredient_name).first()
    if inventoryItem is None:
        if quantity_n <= 0:
            return jsonify({"error": "Invalid quantity"}), 400
        newItem = InventoryIngredient(user=user, name=ingredient_name, quantity=quantity_n, measureType=measureType)
        user.addInventory(newItem)
        session.commit()
    else:
        inventoryItem.quantity = quantity_n+inventoryItem.quantity
        if inventoryItem.quantity <= 0:
            user.removeInventory(inventoryItem)
        session.commit()
    return jsonify(user.to_dict()), 200
    
