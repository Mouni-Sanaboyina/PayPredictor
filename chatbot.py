
import streamlit as st
import google.generativeai as genai

# API key (hardcoded)
API_KEY = "AIzaSyD25SGMAtLg7WlgIisJo6RnKcMMYhKl0fc"

# Configure the generative model
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize chat session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Streamlit app title
st.title("🤖 PayPredictorChatbot - Your Career AI Assistant")
st.write("Welcome to PayPredictor! How can i help you?")

# Initialize messages in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Say something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get chatbot response
    response = st.session_state.chat.send_message(prompt)

    # Add chatbot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    with st.chat_message("assistant"):
        st.markdown(response.text)
