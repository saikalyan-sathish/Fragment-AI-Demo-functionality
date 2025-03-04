import json

def process_command(self, command):
    response = self.llm.generate(command)  # Assuming this calls the LLM API

    try:
        # Ensure it's valid JSON
        parsed_result = json.loads(response)
        
        # Validate required fields
        if not all(k in parsed_result for k in ["task", "time", "date"]):
            raise ValueError("Missing required fields in JSON response.")

        return json.dumps(parsed_result, indent=2)  # Pretty print JSON for Streamlit
    except json.JSONDecodeError:
        raise ValueError("Model did not return a valid JSON. Try rephrasing.")
