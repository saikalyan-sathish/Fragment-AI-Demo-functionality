import streamlit as st
from ai_functionality import get_raw_output  # Import AI functionality
from parser import ReminderOutputParser      # Import JSON output parser

# Streamlit app
st.title("Reminder Extractor")
st.write("Note: Please specify the date in absolute terms (e.g., 'December 25th'), or omit it for today.")

# Text input for user prompt
user_input = st.text_input("Enter your reminder request (e.g., 'set a reminder for 3pm')")

# Button to process the input
if st.button("Extract"):
    if user_input:
        with st.spinner("Extracting information..."):
            # Get raw output from AI functionality
            raw_output = get_raw_output(user_input)
            
            # Parse raw output to JSON using the parser
            parser = ReminderOutputParser()
            json_output = parser.parse(raw_output)
            
            # Display the JSON output
            st.json(json_output)
    else:
        st.write("Please enter a reminder request.")