import requests
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import os
import json

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

def get_raw_output(user_input):
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Construct the prompt
    prompt = f"""<s>[INST] You are an AI assistant that can set reminders. Today's date: {current_date}

    Available function:
    set_reminder(time, task, date)

    User request: {user_input}

    Respond with either:
    1. JSON function call (example below)
    2. Natural language response

    Example function call:
    {{
        "function_call": {{
            "name": "set_reminder",
            "arguments": {{
                "time": "3:30 PM",
                "task": "Meeting",
                "date": "2023-12-25"
            }}
        }}
    }} [/INST]"""
    
    # API call parameters
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.3,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract generated text
        if isinstance(result, list) and 'generated_text' in result[0]:
            return result[0]['generated_text']
        return result
        
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error: {err}")
    except json.JSONDecodeError:
        st.error("Invalid JSON response")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    return None