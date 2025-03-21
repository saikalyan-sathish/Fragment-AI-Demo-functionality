import streamlit as st
from workflow import workflow_instance
from voice_input import get_voice_input
import agendas_db  # Import your agenda_db module

st.title("Advanced Reminder Agent")

# Initialize session state for user input if not set
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# Handle transcribed text from query params
if 'transcribed' in st.query_params:
    st.session_state['user_input'] = st.query_params['transcribed']
    st.query_params.clear()

# Button to record voice input **before** rendering text_input
if st.button("Record Voice"):
    with st.spinner("Listening..."):
        try:
            transcribed_text = get_voice_input()
            if "Error" not in transcribed_text:
                # 🔥 Update session state without causing widget conflicts
                st.session_state["user_input"] = transcribed_text
                st.success("✅ Voice input recorded and transcribed!")
            else:
                st.error(transcribed_text)
        except Exception as e:
            st.error(f"❌ Error in voice input: {e}")

# 🔥 Render text_input without `value` parameter (Fixes warning)
user_input = st.text_input("Enter your reminder request:", key="user_input")

# Process button
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
        st.warning("Please enter a reminder request.")
