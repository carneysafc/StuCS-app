import streamlit as st
import os
from phi.assistant import Assistant
from phi.llm.ollama import Ollama
from phi.tools.yfinance import YFinanceTools
from phi.tools.serpapi_tools import SerpApiTools
from toolz import identity

# Set the Streamlit page configuration
st.set_page_config(page_title="Stu Customer Service", page_icon="📷")

# Access the SerpApi API key from Streamlit secrets
serpapi_api_key = st.secrets["SERPAPI_API_KEY"]

# Function to get the assistant instance with selected tools
def get_assistant(tools):
    return Assistant(
        name="llama3_assistant",
        llm=Ollama(model="llama3"),
        tools=tools,
        description="You are a helpful assistant that can access specific tools based on user selections.",
        show_tool_calls=True,
        debug_mode=True,
        add_datetime_to_instructions=True,
    )

st.title("Stu Customer Service AI Assistant")
st.markdown("""
This app demonstrates function calling with the local Llama3 model using Ollama.
Select tools in the sidebar and ask relevant questions!
""")

# Sidebar for tool selection
st.sidebar.title("Tool Selection")
use_yfinance = st.sidebar.checkbox("YFinance (Stock Data)", value=True)
use_serpapi = st.sidebar.checkbox("SerpAPI (Web Search)", value=True)

# Initialize the list of tools based on user selection
tools = []
if use_yfinance:
    tools.append(YFinanceTools(stock_price=True, company_info=True))
if use_serpapi:
    tools.append(SerpApiTools(api_key=serpapi_api_key))  # Pass the API key to the tool

# Initialize the assistant with the selected tools
if "assistant" not in st.session_state or st.session_state.get("tools") != tools:
    st.session_state.assistant = get_assistant(tools)
    st.session_state.tools = tools
    st.session_state.messages = []  # Reset messages when tools change

# Display current tool status in the sidebar
st.sidebar.markdown("### Current Tools:")
st.sidebar.markdown(f"- YFinance: {'Enabled' if use_yfinance else 'Disabled'}")
st.sidebar.markdown(f"- SerpAPI: {'Enabled' if use_serpapi else 'Disabled'}")

# Display chat messages
for message in st.session_state.get("messages", []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for user prompts
if prompt := st.chat_input("Ask a question based on the enabled tools"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        response_container = st.empty()
        response = ""
        for chunk in st.session_state.assistant.run(prompt):
            response += chunk
            response_container.write(response + "  ")
        response_container.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
