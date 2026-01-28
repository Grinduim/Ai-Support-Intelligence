import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def openai_chat(system: str, user: str, model: str = "gpt-4o-mini") -> str:
    """
    Call OpenAI chat API with system and user prompts.
    
    Args:
        system (str): System prompt for context and behavior.
        user (str): User prompt for the query.
        model (str): Model identifier (default: gpt-4o-mini).
        
    Returns:
        str: The assistant's response text.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content
