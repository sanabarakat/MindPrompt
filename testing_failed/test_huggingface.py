import os
import aisuite as ai

# Either set the environment variables or define the parameters below.
# Setting the parameters in ai.Client() will override the environment variable values.

HF_TOKEN = os.getenv("HF_TOKEN")  # Replace with your Hugging Face API token.

client = ai.Client()

model = "huggingface:meta-llama/Llama-3.1-8B"  # Replace with your model's identifier.

def generate_prompt():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Suggest a thoughtful journaling prompt for self-reflection."},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return (response.choices[0].message.content)