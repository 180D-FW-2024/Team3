from together import Together
import re
import dotenv
import os

dotenv.load_dotenv()

options = [
    "next instruction",
    "previous instruction",
    "repeat instruction",
    "list ingredients",
    "current temperature",
    "time remaining",
    "start timer",
    "stop timer",
    "add ingredient",
    "add ingredient with camera",
    "remove ingredient",
    "recommend recipe",
    "measure ingredient",
    "add allergy",
    "remove allergy",
    "scan login",
    "question"
]

client = Together()
def send_command(command) -> str:
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{
            "role": "system",
            "content": """You are a cooking assistant, who will take in user commands as text and respond with the number it corresponds to.\n
            Here is the list of possible commands, each command MUST map to one of these:""" + "\n".join([f"{option}" for option in options]) +
            "Respond with the above text that each of the following user-provided commands corresponds to."
        },
        {
            "role": "user",
            "content": command
        }
        ],
        max_tokens=32,
        temperature=0.2,
        top_p=0.7,
        top_k=50,
        repetition_penalty=0,
        stop=["<|eot_id|>","<|eom_id|>"],
        stream=True
    )
    if response is None:
        return None
    try:
        results = []
        for token in response:
            print(token.choices[0].delta.content, end='', flush=True)
            results.append(token.choices[0].delta.content.strip())
        return results
    except Exception as e:
        print(f"Error: {e}")
        return None

def answer_question(question, contextIngredients=None, contextAllergies=None, contextRecipe=None) -> str:
    if not question:
        return None
    
    systemPrompt = """You are a cooking assistant, who will answer the following user question regarding cooking. 
                      IF THE QUESTION IS UNRELATED TO COOKING, RETURN ONLY 'INVALID'."""

    if contextIngredients:
        systemPrompt += f"CONTEXT: The following user inventory ingredients are available: {contextIngredients}"
    if contextAllergies:
        systemPrompt += f"CONTEXT: The following user allergies are available: {contextAllergies}"
    if contextRecipe:
        systemPrompt += f"CONTEXT: The following recipe is being used: {contextRecipe}"

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{
            "role": "system",
            "content": systemPrompt
        },
        {
            "role": "user",
            "content": question
        }
        ],
        max_tokens=128,
        temperature=0.5,
        top_p=0.7,
        top_k=50,
        repetition_penalty=0,
        stop=["<|eot_id|>","<|eom_id|>"],
        stream=True
    )
    if response is None:
        return None
    try:
        results = []
        for token in response:
            print(token.choices[0].delta.content, end='', flush=True)
            results.append(token.choices[0].delta.content.strip())
        outputString = "".join([re.sub(r'[^\w;]+', '', token) for token in results]).strip().lower()
        return outputString
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def standardizeIngredient(name) -> dict:
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{
            "role": "system",
            "content": """Take the user-provided ingredient, and return a standard form of the ingredient. The output should consist
            of three parts, separated by semicolons ';'. The first part should be the name of the ingredient in singular (NOT plural)
            form as one word if possible. The second part should be a number representing the measure quantity specified as a number,
            and if count is used specify the number count of ingredient. The third part should be the unit of measure type (ex. grams,
            milliliters, etc.), if there is no unit of measure then it should be returned as 'count'. THERE MUST ALWAYS BE 3 PARTS."""
        },
        {
            "role": "user",
            "content": name
        }
        ],
        max_tokens=512,
        temperature=0.7,
        top_p=0.3,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>","<|eom_id|>"],
        stream=True
    )
    if response is None:
        return None
    try:
        results = []
        for token in response:
            print(token.choices[0].delta.content, end='', flush=True)
            results.append(token.choices[0].delta.content.strip())
        print("Direct results",results)
        outputString = "".join([re.sub(r'[^\w;]+', '', token) for token in results]).strip().lower()
        print("Output String", outputString)
        outputSections = outputString.split(";")
        if len(outputSections) < 3:
            measureUnit = "count"
        else:
            measureUnit = outputSections[2].strip()
        return {"ingredient_name": outputSections[0].strip(), "quantity": int(outputSections[1].strip()), "measureUnit": measureUnit}
    except Exception as e:
        print(f"Error: {e}")
        return None