from together import Together

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
    "remove ingredient"
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
        max_tokens=512,
        temperature=0.7,
        top_p=0.7,
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
        return results
    except Exception as e:
        print(f"Error: {e}")
        return None
    