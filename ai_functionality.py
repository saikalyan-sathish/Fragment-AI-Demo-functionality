import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
API_KEY = os.getenv('HUGGINGFACE_API_KEY')

if API_KEY is None:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file")

def get_raw_output(user_input: str) -> str:
    """
    Generate a raw response using the Hugging Face Inference API for the Mistral 7B Instruct model.
    
    Args:
        user_input (str): The user's reminder request (e.g., "Remind me to call John tomorrow at 3 PM").
    
    Returns:
        str: The model's response, ideally a JSON string with 'time', 'task', and 'date'.
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
    
    # Set up the API endpoint and headers
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Set up the payload for the API request
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 150,          # Allow enough tokens for JSON output
            "num_return_sequences": 1,  # Return a single response
            "do_sample": False          # Use greedy decoding for consistency
        }
    }
    
    # Make the API call
    response = requests.post(api_url, json=payload, headers=headers)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    # Extract the generated text from the response
    generated_data = response.json()
    if not generated_data or 'generated_text' not in generated_data[0]:
        raise Exception("Unexpected API response format")
    
    generated_text = generated_data[0]['generated_text']
    
    # Trim the prompt from the generated text if necessary
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):].strip()
    
    return generated_text