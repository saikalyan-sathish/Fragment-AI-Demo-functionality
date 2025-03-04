from langchain.prompts import PromptTemplate

# Define the system prompt to enforce JSON structure
SYSTEM_PROMPT = """
You are an intelligent scheduling assistant. 
Your task is to extract the task, time, and date from user input and return a JSON object.
Your response **MUST** be in this exact format:

{
  "task": "<task_description>",
  "time": "<HH:MM AM/PM>",
  "date": "<YYYY-MM-DD>"
}

Do not add any extra text, explanations, or markdown.
"""

# Create a LangChain PromptTemplate to structure the input
PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["command"],
    template=SYSTEM_PROMPT + "\nUser Input: {command}\nResponse:"
)
