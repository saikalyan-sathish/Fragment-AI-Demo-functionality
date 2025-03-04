import asyncio
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from prompt_templates import PROMPT_TEMPLATE  # Import the prompt template

class SchedulingAgent:
    def __init__(self, model_name="google/flan-t5-base", max_length=200):
        """
        Initializes the scheduling agent with a text2text-generation model.
        """
        # Load the model with specified parameters
        pipe = pipeline("text2text-generation", model=model_name, max_length=max_length)
        
        # Wrap the pipeline in a LangChain-compatible LLM
        self.llm = HuggingFacePipeline(pipeline=pipe)
        
        # Set up the LLMChain with the system prompt
        self.chain = LLMChain(llm=self.llm, prompt=PROMPT_TEMPLATE)
    
    async def process_command(self, command: str) -> str:
        """
        Processes the natural language command and returns a JSON string
        with keys: task, time, and date.
        """
        return await asyncio.to_thread(self.chain.invoke, {"command": command})

async def main():
    """
    Main function to run the scheduling agent and process a test command.
    """
    agent = SchedulingAgent()
    
    # Example user command
    command = "Remind me to call John at 3:30 PM on March 5th."
    
    # Process the command and print the structured response
    response = await agent.process_command(command)
    print(response)

# Run the script in an async event loop
if __name__ == "__main__":
    asyncio.run(main())
