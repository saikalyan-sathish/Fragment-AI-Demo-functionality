from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFacePipeline
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

# Load model and pipeline with caching
@st.cache_resource
def load_model():
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_API_KEY)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, token=HF_API_KEY)
    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=100
    )
    return pipe

# Create prompt template (moved outside function for reuse)
template = """You are an AI assistant that can interact with the user and call functions based on their requests.

Available functions:

set_reminder(time, task, date): Sets a reminder with the given time, task, and date.

- time: string, the time of the reminder (e.g., "3pm", "10:30 am")
- task: string, the description of the task
- date: string, the date in YYYY-MM-DD format

If the user's request is to set a reminder, you should call this function with the appropriate parameters. If the user does not specify a date, use today's date: {today_date}

Your response should be in the following format:

If you are calling a function, output a JSON object with the key "function_call" containing the function name and arguments.

Otherwise, output a regular response to the user.

For example:

{
  "function_call": {
    "name": "set_reminder",
    "arguments": {
      "time": "3pm",
      "task": "Meeting with John",
      "date": "2023-12-25"
    }
  }
}

Or, if no function is called:

"Alright, I've got it."

Now, the user's request is: {query}

Remember, date should be in YYYY-MM-DD format.

Today's date is {today_date}."""
prompt = PromptTemplate(
    input_variables=["query", "today_date"],
    template=template
)

# Function to get raw output
def get_raw_output(user_input):
    pipe = load_model()  # Initialize pipeline here
    hf_pipeline = HuggingFacePipeline(pipeline=pipe)
    chain = prompt | hf_pipeline
    current_date = datetime.now().strftime("%Y-%m-%d")
    raw_output = chain.invoke({"query": user_input, "today_date": current_date})
    return raw_output