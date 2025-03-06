# Flask script for handling incoming requests
from quart import Quart, jsonify, request, current_app
from quart_cors import cors
from sqlalchemy import create_engine, not_, func, or_, and_, exists, text
from sqlalchemy.orm import sessionmaker, aliased
from .models.userModel import User, TelegramRegistration
from .models.recipeModel import Recipe
from .models.ingredientModel import Allergy, RecipeIngredient, InventoryIngredient
from .models.helpers import MeasureType, standardize, getMeasureType
# from ..LLM.LLMAgent import send_command, options, standardizeIngredient
from .LLMAgent import send_command, options, standardizeIngredient
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder
import subprocess
import re
import dotenv
import random
import string
import os
import requests



dotenv.load_dotenv()
PORT_NUMBER = os.getenv("PORT_NUMBER")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

# Run test_db.py to test database, remove on database completion
subprocess.run(["python3", "/app/app/setup_db.py"])

engine = create_engine('sqlite:///raspitouille.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

app = Quart(__name__)
cors(app)

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()


@app.before_serving
async def setup():
    # Initialize bot application
    await bot_app.initialize()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Teardown previous webhook
    await bot_app.bot.delete_webhook()
    print("DELETE WEBHOOK")
    
    # Webhook setup
    await bot_app.bot.set_webhook(
        url=f"{BACKEND_URL}/webhook",
        allowed_updates=Update.ALL_TYPES
    )
    print("SET WEBHOOK")

async def send_message(chat_id, text):
    return requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={text}").json()

async def start(update, context):
    print("Processing start command: " + str(update))
    try:
        joinCode = update.message.text.split(' ')[-1]
        print('Filtering for join code: ' + joinCode)
        joinRelation = session.query(TelegramRegistration).filter_by(user_code=joinCode).first()
        print("Join relation: " + str(joinRelation))
        if joinRelation is None:
            await send_message(chat_id=update.message.chat_id, text="Invalid join code")
            return
    except Exception as e:
        print(e)
        await send_message(chat_id=update.message.chat_id, text="Invalid join code")
        return
    
    try:
        rows = session.query(User).filter_by(id=joinRelation.user_id).update({"telegram_id": update.message.chat_id})
        if rows == 0:
            await send_message(chat_id=update.message.chat_id, text="No matching user found")
            return
        print("Updated user: " + str(session.query(User).filter_by(id=joinRelation.user_id).first()))
        await send_message(chat_id=update.message.chat_id, text="Congratulations! Your account has been successfully linked")
    except Exception as e:
        print(e)
        await send_message(chat_id=update.message.chat_id, text="Error linking account")
        return

def echo(update, context):
    update.message.reply_text(update.message.text)

def help(update, context):
    update.message.reply_text("Hello! I am Raspitouille's notification service. Use Raspitouille to ")
    return 'ok', 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    print("Received webhook update")
    # Get the update
    json_data = await request.get_json() 
    update = Update.de_json(json_data, bot_app.bot)
    print("Received update: " + str(update))
    
    # Process the update
    await bot_app.process_update(update)

    return 'ok', 200


@app.route('/send-alert', methods=['POST'])
async def send_alert():
    """
    Send an alert to the user with the given ID

    Parameters:
        userId (int): The ID of the user to send the alert to
        message (str): The message to send

    Returns:
        A JSON object with a status code and a message

    Raises:
        404: The user was not found
        400: The user is not registered with Telegram
    """
    print("Received alert update")
    userId = request.args.get('userId')
    message = re.sub(r'\%20', ' ', request.args.get('message', default=''))
    print("Sending alert to user " + userId + " with message " + message)
    row = session.query(User).filter_by(id=userId).first()
    if row is None:
        return jsonify({"error": "User not found"}), 404
    if row.telegram_id is None:
        return jsonify({"error": "User is not registered with Telegram"}), 400
    await send_message(chat_id=row.telegram_id, text=message)
    return jsonify({"response": "Alert sent"}), 200

@app.route("/command/<command>", methods=['GET'])
def map_command(command):
    """
    Handles a GET request to /command/<command>.  Maps the given command to its
    corresponding string in the list of possible commands, if it exists.
    Otherwise, returns a 400 error with a JSON object containing the error
    message "Command Not Recognized".  If the API does not respond, returns a
    500 error with a JSON object containing the error message "No API Response".

    Parameters
    ----------
    command : str
        The command to map to its corresponding string

    Returns
    -------
    JSON object
        The mapped command string, or an error message if the command does not
        exist or if the API does not respond

    Status Codes
    ------------
    200 : The command was successfully mapped
    400 : The command was not recognized
    500 : The API did not respond
    """
    output = send_command(re.sub(r'[\_\s\-]+', ' ', command.strip()))
    if output is None:
        return jsonify({ "response": "No API Response" }), 500
    outputString = " ".join([re.sub(r'[^a-zA-Z]+', '', token) for token in output]).strip().lower()
    print("OUTPUT STRING COMMAND: " + outputString)
    if outputString not in options:
        return jsonify({ "response": "Command Not Recognized" }), 400
    else:
        return jsonify({ "response": outputString }), 200

'''
How would user flow work below?
Essentially, user would send this get request to return a random number associated in a table
with the provided phone number.

When the request is made, add to the registration table and keep a datetime value to handle invalid codes

1) If the phone number does not exist in the database, return a 404 error
2) If the phone number is not associated with a valid telegram id, go through with the process
3) If the phone number is associated with a valid telegram id, still go through with the process,
just overwrite already existing telegram id on response

'''
@app.route("/connect-telegram", methods=['GET'])
def connect_telegram():
    try:
        print("Request args: " + str(request.args))
        phone_number = re.sub(r'[^0-9]', '',request.args.get('phoneNumber', default=''))
        print("PHONE NUMBER: " + phone_number)
        if not phone_number:
            return jsonify({"error": "Phone number not provided"}), 400
        """
        Handles a GET request to /connect-telegram?phoneNumber=<phone_number>.  Generates a
        random 15-character alphanumeric code and associates it with the given
        phone number in the TelegramRegistration table.  If the phone number does
        not exist in the database, returns a 404 error with a JSON object
        containing the error message "User not found".  If the phone number is
        associated with a valid telegram id, still go through with the process,
        just overwrite already existing telegram id on response.

        Parameters
        ----------
        phone_number : str
            The phone number to associate with the generated code

        Returns
        -------
        JSON object
            The generated code, or an error message if the phone number does not
            exist in the database

        Status Codes
        ------------
        200 : The code was successfully generated and associated with the given phone number
        404 : The phone number does not exist in the database
        """
        connectingUser = session.query(User).filter_by(phone_number=phone_number).first()
        if connectingUser is None:
            return jsonify({"error": "User not found"}), 404
        
        joinCode = ''.join(random.choices(string.ascii_letters, k=15))
        while session.query(TelegramRegistration).filter_by(user_code=joinCode).first() is not None:
            joinCode = ''.join(random.choices(string.ascii_letters, k=15))

        session.add(TelegramRegistration(user_id=connectingUser.id, user_code=joinCode))
        session.commit()
        print("SUCCESS generating join code: " + joinCode)

        return jsonify({"join_code": joinCode}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/register-telegram/<join_code>/<telegram_id>", methods=['GET'])
def register_telegram(join_code, telegram_id):
    """
    Handles a GET request to /register-telegram/<join_code>/<telegram_id>.  
    Removes all join codes that are over 30 minutes old, and then checks if the
    given join code is valid.  If it is, associates the telegram_id with the
    user that generated the join code and returns a 200 status code with a JSON
    object containing the response "Registration successful".  If the join code
    is invalid, returns a 400 status code with a JSON object containing the
    error message "Invalid join code".

    Parameters
    ----------
    join_code : str
        The join code generated by the user
    telegram_id : str
        The telegram id to associate with the join code

    Returns
    -------
    JSON object
        The response, either "Registration successful" or "Invalid join code"

    Status Codes
    ------------
    200 : The registration was successful
    400 : The join code is invalid
    """
    session.query(TelegramRegistration).filter(TelegramRegistration.generation_time + text("INTERVAL 30 MINUTE") > func.now() ).delete()
    registration = session.query(TelegramRegistration).filter_by(join_code=join_code).first()
    if registration is None:
        return jsonify({"error": "Invalid join code"}), 400
    user = session.query(User).filter_by(id=registration.user_id).first()
    user.telegram_id = telegram_id
    session.commit()
    return jsonify({"response": "Registration successful"}), 200
    

'''
USER FLOW FOR ACCOUNT CREATION / LOGIN 



CASE 1: User is already logged in with phone number on device

This really doesn't do anything new FOR LOGIN.

FOR TELEGRAM we can have the user input phone number (registered on the raspi) and then link their account as normal.

User can logout through a logout command.


CASE 2: User is not logged in with phone number on device

Originally, this triggers the random username creation process on Raspi (OLD INVALID LOGIC)

1) Raspi goes into a cycle for looking for QR code, and upon scanning it loads as the username directly into the user_config file

*If the username already exists in the database, logging in with phone number will function as normal, otherwise we generate a user associated with the phone number


'''

@app.route("/", methods=['GET'])
def ping():
    return jsonify({"response": "pong"}), 200

@app.rout("/get-allergies-ingredients", methods=['GET']) # "/get-allergies-ingredients?userId="
def get_allergies_ingredients():
    userId = request.args.get('userId')
    user = session.query(User).filter_by(id=userId).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    userDict = user.to_dict()
    return jsonify({"allergies": ", ".join(userDict["allergies"]), "ingredients": ", ".join(userDict["inventory"])}), 200

@app.route("/create-user", methods=['POST'])
def create_user():
    """
    Handles a POST request to /create-user?username=<username>.  Creates a new user in
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
    200 : The user already exists in the database
    404 : No username provided
    """
    username = request.args.get('username')
    if username is None:
        return jsonify({"error": "No username provided"}), 404
    phoneNumber = re.sub(r'[^0-9]','',request.args.get('phone_number', ''))
    username = standardize(username)
    if session.query(User).filter_by(username=username).first() is not None:
        return jsonify({"message": "User already exists"}), 200
    firstName = request.args.get('firstName')
    session.add(User(username=username, first_name=(firstName if firstName is not None else ""), phone_number=phoneNumber))
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
    201 : The user exists in the database and the allergy was added
    200 : The user exists in the database and the allergy was already added
    404 : The user does not exist in the database
    """
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    allergy = session.query(Allergy).filter_by(name=standardize(allergy_name)).first()
    if allergy is None:
        allergy = Allergy(name=allergy_name)
    if allergy not in user.allergies:
        user.addAllergy(allergy)
        session.commit()
        return jsonify(user.to_dict()), 201
    else:
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
    allergy = session.query(Allergy).filter_by(name=standardize(allergy_name)).first()
    if allergy is None:
        return jsonify({"error": "Allergy not found"}), 404
    user.removeAllergy(allergy)
    session.commit()
    return jsonify(user.to_dict()), 200

@app.route("/get-recipe/<recipe_id>", methods=['GET'])
def get_recipe(recipe_id):
    """
    Handles a GET request to /get-recipe/<recipe_id>.  Returns a JSON object
    containing the recipe with the given ID.

    Parameters
    ----------
    recipe_id : int
        The ID of the recipe to retrieve

    Returns
    -------
    JSON object
        The requested recipe as a JSON object

    Status Codes
    ------------
    200 : The recipe exists in the database
    404 : The recipe does not exist in the database
    """
    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify(recipe.to_dict()), 200

@app.route("/suggest-recipes/<user_id>", methods=['GET'])
def suggest_recipes(user_id):
    """
    Handles a GET request to /suggest-recipes/<user_id>.  Returns a JSON object
    containing a list of recipes that are valid for the given user.

    Parameters
    ----------
    user_id : int
        The ID of the user to suggest recipes for

    Returns
    -------
    JSON object
        A list of recipes that are valid for the given user

    Status Codes
    ------------
    200 : The user exists in the database and the recipes were suggested
    404 : The user does not exist in the database
    """
    
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    userAllergyNames = [allergy.name for allergy in user.allergies]
    userInventoryMap = {} 
    for ingredient in user.inventory:
        userInventoryMap[ingredient.name] = ingredient.quantity

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
        inventoryItem = InventoryIngredient(user=user, name=ingredient_name, quantity=quantity_n, measureType=measureType)
        user.addInventory(inventoryItem)
        session.commit()
    else:
        inventoryItem.quantity = quantity_n+inventoryItem.quantity
        if inventoryItem.quantity <= 0:
            user.removeInventory(inventoryItem)
        session.commit()
    print(inventoryItem.to_dict())
    return jsonify(inventoryItem.to_dict()), 200

'''
Specialized route for adding an ingredient through user commands as natural language
'''
@app.route("/add-ingredient/<user_id>/<ingredientString>", methods=['PUT'])
def add_ingredient(user_id, ingredientString):
    try:
        ingredientDict = standardizeIngredient(re.sub(r'\%20', ' ', ingredientString))
        if ingredientDict is None:
            return jsonify({"error": "Invalid ingredient"}), 400
        measureUnit = ingredientDict["measureUnit"]
        ( measure, multiplier )= getMeasureType(measureUnit)
        print("ingredientDict: " + str(ingredientDict), "measure:" + str(measure.name), "multiplier:" + str(multiplier))
        additionJson = modify_inventory(user_id, ingredientDict["ingredient_name"], ingredientDict["quantity"]*multiplier, measure.name, "add")
        return additionJson
    except Exception as e:
        print(e)
        return jsonify({"error": "Addition Failure"}), 400

'''
Specialized route for removing an ingredient through user commands as natural language
'''
@app.route("/remove-ingredient/<user_id>/<ingredientString>", methods=['PUT'])
def remove_ingredient(user_id, ingredientString):
    try:
        ingredientDict = standardizeIngredient(re.sub(r'\%20', ' ', ingredientString))
        if ingredientDict is None:
            return jsonify({"error": "Invalid ingredient"}), 400
        measureUnit = ingredientDict["measureUnit"]
        ( measure, multiplier )= getMeasureType(measureUnit)
        print("ingredientDict: " + str(ingredientDict), "measure:" + str(measure.name), "multiplier:" + str(multiplier))
        removalJson = modify_inventory(user_id, ingredientDict["ingredient_name"], ingredientDict["quantity"]*multiplier, measure.name, "remove")
        return removalJson
    except Exception as e:
        print(e)
        return jsonify({"error": "Removal Failure"}), 400

if __name__ == "__main__":
   print("Starting server on port " + PORT_NUMBER)
   app.run(port=int(PORT_NUMBER))
