import streamlit as st
from workflow import workflow_instance
from voice_input import get_voice_input_html
import agendas_db  # Import your agenda_db module

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
                
                # Call agenda_db functionality
                try:
                    agendas_db.save_reminder(result["parsed_data"])
                    st.write("Reminder stored successfully through agenda_db")
                except Exception as e:
                    st.error(f"Error storing reminder: {e}")
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        st.warning("Please enter a reminder request")
