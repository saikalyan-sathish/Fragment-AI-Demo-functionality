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
template = """You are a reminder extraction assistant. Extract the time, task, and date from the following reminder request:
{query}

Respond strictly in this format:
Time: [time]
Task: [task]
Date: [date]

If no date is mentioned, use today's date: {today_date}"""
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