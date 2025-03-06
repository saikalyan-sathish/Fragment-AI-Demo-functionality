import streamlit as st
from workflow import workflow_instance

st.title("Advanced Reminder Agent")
user_input = st.text_input("Enter your reminder request:")

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
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        st.warning("Please enter a reminder request")