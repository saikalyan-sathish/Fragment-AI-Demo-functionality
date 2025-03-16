import streamlit as st
from workflow import workflow_instance
from voice_input import get_voice_input_html
from pymongo import MongoClient

# Initialize MongoDB connection once at app start
client = MongoClient("mongodb://localhost:27017/")
db = client["reminder_database"]
reminders_collection = db["reminders"]

st.title("Advanced Reminder Agent")

# Handle transcribed text from query params
if 'transcribed' in st.query_params:
    st.session_state['user_input'] = st.query_params['transcribed']
    st.query_params.clear()

# Text input linked to session state
user_input = st.text_input("Enter your reminder request:", key='user_input')

# Add the voice input component
st.components.v1.html(get_voice_input_html(), height=50)

if st.button("Process"):
    if user_input:
        with st.spinner("Processing your request..."):
            result = workflow_instance.invoke({
                "user_input": user_input,
                "retries": 0
            })
            if "result" in result:
                st.success("✅ Reminder Created!")
                st.json(result["parsed_data"])
                 
                # Store in MongoDB using pre-initialized collection
                try:
                    insert_result = reminders_collection.insert_one(result["parsed_data"])
                    st.write(f"Reminder stored successfully. ID: {insert_result.inserted_id}")
                except Exception as e:
                    st.error(f"Error storing reminder: {e}")
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        st.warning("Please enter a reminder request")
