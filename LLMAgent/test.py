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
for token in response:
    if hasattr(token, 'choices'):
        print(token.choices[0].delta.content, end='', flush=True)