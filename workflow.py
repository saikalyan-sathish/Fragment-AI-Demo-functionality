from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from ai_functionality import get_raw_output
from parser import ReminderOutputParser

# Define the AgentState with default values for clarity
class AgentState(TypedDict):
    user_input: str
    raw_response: Optional[str] = None
    parsed_data: Optional[dict] = None
    error: Optional[str] = None
    result: Optional[str] = None
    retries: int = 0

class ReminderWorkflow:
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        self._setup_graph()
    
    def _setup_graph(self):
        # Add nodes to the workflow
        self.workflow.add_node("generate", self.generate_response)
        self.workflow.add_node("parse", self.parse_output)
        self.workflow.add_node("execute", self.execute_function)
        self.workflow.add_node("handle_error", self.handle_error)
        self.workflow.add_node("retry", self.retry)  # New retry node
        
        # Define the workflow structure
        self.workflow.set_entry_point("generate")
        self.workflow.add_edge("generate", "parse")
        self.workflow.add_conditional_edges(
            "parse",
            self.decide_next_step,
            {
                "success": "execute",
                "retry": "retry",    # Updated to point to the retry node
                "failure": "handle_error"
            }
        )
        self.workflow.add_edge("retry", "generate")  # Retry loops back to generate
        self.workflow.add_edge("execute", END)
        self.workflow.add_edge("handle_error", END)
        
        # Compile the graph
        self.graph = self.workflow.compile()
    
    def generate_response(self, state: AgentState):
        """Generate a raw response based on user input."""
        return {"raw_response": get_raw_output(state["user_input"])}
    
    def parse_output(self, state: AgentState):
        """Parse the raw response into structured data."""
        try:
            parser = ReminderOutputParser()
            return {"parsed_data": parser.parse(state["raw_response"])}
        except Exception as e:
            return {"error": str(e)}
    
    def execute_function(self, state: AgentState):
        """Execute the action (e.g., store the reminder)."""
        # Replace with actual database/store integration
        print(f"Storing reminder: {state['parsed_data']}")
        return {"result": "Reminder set successfully"}
    
    def handle_error(self, state: AgentState):
        """Handle any errors that occurred."""
        return {"error": state.get("error", "Unknown error")}
    
    def retry(self, state: AgentState):
        """Increment retries and return the updated state."""
        state["retries"] += 1
        return state
    
    def decide_next_step(self, state: AgentState):
        """Decide the next step based on the current state."""
        if state.get("error"):
            return "retry" if state["retries"] < 2 else "failure"
        return "success" if state["parsed_data"] else "failure"

# Singleton instance
workflow_instance = ReminderWorkflow().graph