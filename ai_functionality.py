import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import random
from langchain_huggingface import HuggingFaceEndpoint
from agendas_db import save_reminder  # Import MongoDB function

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

def get_raw_output(user_input: str, max_retries: int = 3, initial_delay: int = 5) -> dict:
    """
    Generate a raw response using the Hugging Face Inference API and store it in MongoDB.
    
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
    
    prompt = f"""Today is {current_date}. Generate a JSON object with 'time', 'task', and 'date' fields for a reminder based on the following request: {user_input}

For example, if the request is "Remind me to call John tomorrow at 3 PM", you should output:
{{
    "time": "3:00 PM",
    "task": "call John",
    "date": "{(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}"
}}"""
    
    for attempt in range(max_retries):
        try:
            generated_text = llm(prompt)
            
            # Ensure the response is a valid dictionary
            reminder_data = eval(generated_text) if isinstance(generated_text, str) else generated_text

            if not isinstance(reminder_data, dict) or not all(k in reminder_data for k in ["time", "task", "date"]):
                raise ValueError("Invalid JSON response format from LLM.")

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
