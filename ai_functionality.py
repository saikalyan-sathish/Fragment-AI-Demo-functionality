# ai_functionality.py
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import random
from langchain_huggingface import HuggingFaceEndpoint

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
API_KEY = os.getenv('HUGGINGFACE_API_KEY')

if API_KEY is None:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file")

# Define the LLM instance using HuggingFaceEndpoint
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    task="text-generation",
    max_new_tokens=4096,
    do_sample=False,
    return_full_text=False,  # Ensures only generated text is returned
    huggingfacehub_api_token=API_KEY
)

def get_raw_output(user_input: str, max_retries: int = 3, initial_delay: int = 5) -> str:
    """
    Generate a raw response using the Hugging Face Inference API via HuggingFaceEndpoint.
    
    Args:
        user_input (str): The user's reminder request (e.g., "Remind me to call John tomorrow at 3 PM").
        max_retries (int): Number of retry attempts if the API request fails (default: 3).
        initial_delay (int): Initial delay in seconds for exponential backoff (default: 5).
    
    Returns:
        str: The model's response, ideally a JSON string with 'time', 'task', and 'date'.
    
    Raises:
        Exception: If all retry attempts fail.
    """
    # Get the current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Craft a prompt instructing the model to output JSON
    prompt = f"""Today is {current_date}. Generate a JSON object with 'time', 'task', and 'date' fields for a reminder based on the following request: {user_input}

For example, if the request is "Remind me to call John tomorrow at 3 PM", you should output:
{{
    "time": "3:00 PM",
    "task": "call John",
    "date": "{(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}"
}}"""
    
    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            # Use the HuggingFaceEndpoint to generate the response
            generated_text = llm(prompt)
            return generated_text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with exception: {e}")
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                raise Exception("All retry attempts failed. Unable to get a response from the API.")