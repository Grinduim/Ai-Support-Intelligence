import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def openai_chat(system: str, user: str, model: str = "gpt-4.1-mini") -> str:
    response = client.responses.create(
        model=model,
        input=[
            {"role":"system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.2,
    )
    return response.output_text
