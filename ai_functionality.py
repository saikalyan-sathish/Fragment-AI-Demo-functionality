import os
import json
import re
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from huggingface_hub import InferenceClient  # Updated import
from agendas_db import save_reminder  # Import MongoDB function

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
API_KEY = os.getenv('HUGGINGFACE_API_KEY')
if API_KEY is None:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file")

# Define the InferenceClient instance
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=API_KEY)

def extract_json(text) -> dict:
    """
    Extracts JSON data from the model response using regex.
    
    Args:
        text: The raw response from the model (either a string or a dictionary).
    
    Returns:
        dict: Extracted JSON object.
    """
    # If already a dictionary, return it directly.
    if isinstance(text, dict):
        return text

    json_match = re.search(r'\{.*?\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            raise ValueError("Extracted JSON is not valid.")
    raise ValueError("No valid JSON found in the model response.")

def get_raw_output(user_input: str, max_retries: int = 3, initial_delay: int = 5) -> dict:
    """
    Generate a structured reminder using the Hugging Face Inference API and store it in MongoDB.
    
    Args:
        user_input (str): The user's reminder request.
        max_retries (int): Number of retry attempts if the API request fails (default: 3).
        initial_delay (int): Initial delay in seconds for exponential backoff (default: 5).
    
    Returns:
        dict: The stored reminder data.
    
    Raises:
        Exception: If all retry attempts fail.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
Today is {current_date}. Generate a JSON object with 'time', 'task', and 'date' fields for a reminder based on the following request: "{user_input}"

For example:
If the request is "Remind me to call John tomorrow at 3 PM", output:
{{
    "time": "3:00 PM",
    "task": "call John",
    "date": "{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}"
}}

Ensure the output is only valid JSON.
"""
    
    for attempt in range(max_retries):
        try:
            response = client.chat_completion(messages=[{"role": "user", "content": prompt}])
            generated_text = response["choices"][0]["message"]["content"]  # Extract response text
            
            reminder_data = extract_json(generated_text)

            if not all(k in reminder_data for k in ["time", "task", "date"]):
                raise ValueError("Missing required fields in response JSON.")

            # Store in MongoDB
            success, inserted_id = save_reminder(reminder_data)
            if success:
                print(f"✅ Reminder stored in MongoDB with ID: {inserted_id}")
            else:
                print("❌ Failed to store reminder in MongoDB.")

            return reminder_data

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                raise Exception("All retry attempts failed. Unable to get a response from the API.")

# Example usage
if __name__ == "__main__":
    user_input = "Remind me to submit the report at 4 PM tomorrow"
    stored_data = get_raw_output(user_input)
    print(f"Final stored data: {stored_data}")
