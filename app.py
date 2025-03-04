from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain.llms import HuggingFacePipeline
from datetime import datetime
import re

# Custom output parser with flexible regex
class ReminderOutputParser(BaseOutputParser):
    def parse(self, text):
        # Flexible patterns for time, task, and date
        time_pattern = r"Time: (\d{1,2}(?::\d{2})?\s*[ap]m|\d{1,2}(?::\d{2})?)"
        task_pattern = r"Task: (.+?)(?=\s*(?:Time:|Date:|$))"
        date_pattern = r"Date: (\d{4}-\d{2}-\d{2}|\d{1,2}(?:st|nd|rd|th)?\s*\w+)"
        
        # Extract time, task, and date
        time = re.search(time_pattern, text, re.IGNORECASE)
        task = re.search(task_pattern, text, re.IGNORECASE)
        date = re.search(date_pattern, text, re.IGNORECASE)
        
        # Format extracted values
        time = time.group(1).strip() if time else None
        task = task.group(1).strip() if task else "Reminder"
        date = date.group(1).strip() if date else datetime.now().strftime("%Y-%m-%d")
        
        # Convert date to standard format (e.g., "25th december" -> "2023-12-25")
        if date and not re.match(r"\d{4}-\d{2}-\d{2}", date):
            try:
                date = datetime.strptime(date, "%dth %B").strftime("%Y-%m-%d")
            except ValueError:
                try:
                    date = datetime.strptime(date, "%d %B").strftime("%Y-%m-%d")
                except ValueError:
                    date = datetime.now().strftime("%Y-%m-%d")
        
        return {"time": time, "task": task, "date": date}

# Load FLAN-T5 model locally
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Create a local pipeline
pipe = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=100
)

# Wrap the pipeline in LangChain's HuggingFacePipeline
hf_pipeline = HuggingFacePipeline(pipeline=pipe)

# Create prompt template
template = """You are a reminder extraction assistant. Extract the time, task, and date from the following reminder request:
{query}

Respond strictly in this format:
Time: [time]
Task: [task]
Date: [date]

If no date is mentioned, use today's date: {today_date}"""

prompt = PromptTemplate(
    input_variables=["query"],
    template=template,
    partial_variables={"today_date": datetime.now().strftime("%Y-%m-%d")}
)

# Create chain
chain = prompt | hf_pipeline

# Function to get user input and process it
def process_user_input():
    while True:
        # Get user input
        user_input = input("\nEnter a reminder request (or type 'exit' to quit): ")
        
        # Exit condition
        if user_input.lower() == "exit":
            print("Exiting...")
            break
        
        # Process the input
        print(f"\nInput: {user_input}")
        raw_output = chain.invoke({"query": user_input})
        print(f"Raw Output: {raw_output}")
        
        # Parse the output
        result = ReminderOutputParser().parse(raw_output)
        print(f"Output: {result}")

# Run the user input loop
if __name__ == "__main__":
    process_user_input()