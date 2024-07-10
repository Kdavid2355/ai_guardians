import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Define a dictionary with model names and their corresponding API keys for OpenAI and Gemini
model_api_keys = {
    "OpenAI GPT-3.5 Turbo": os.getenv("OPENAI_MODEL_API_KEY"),
    "OpenAI GPT-4": os.getenv("OPENAI_MODEL_API_KEY"),
    "Gemini 1.0 Pro": os.getenv("GEMINI_MODEL_API_KEY"),
    "Gemini 1.5 Pro": os.getenv("GEMINI_MODEL_API_KEY"),
}

# Define a dictionary for model names and their corresponding API client information
model_info = {
    "OpenAI GPT-3.5 Turbo": {
        "client": "OpenAI",
        "model": "gpt-3.5-turbo"
    },
    "OpenAI GPT-4": {
        "client": "OpenAI",
        "model": "gpt-4"
    },
    "Gemini 1.0 Pro": {
        "client": "Gemini",
        "model": "gemini-1.0-pro-latest"
    },
    "Gemini 1.5 Pro": {
        "client": "Gemini",
        "model": "gemini-1.5-pro-latest"
    }
}

# Sidebar for selecting model
with st.sidebar:
    model_name = st.selectbox("Select AI Model", list(model_api_keys.keys()))
    api_key = model_api_keys.get(model_name, None)
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[Get a Gemini API key](https://ai.google.dev/gemini-api?gad_source=1&gclid=Cj0KCQjwv7O0BhDwARIsAC0sjWMrACl7mFcrEL6QTXdcvMzgaxZXL9H2ZyI-nebr92JKnJRqGITm2dIaAijYEALw_wcB&hl=ko)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"

st.title("💬 AI Guardians")
st.caption("🚀 2024 한이음 프로젝트 - AI 거버넌스를 고려한 생성형 AI 평가 및 모니터링 기능 개발")

# Initialize the messages in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "AI Guardians에 오신것을 환영합니다. 어떻게 도와드릴까요?", "model": "System"}]
if "model_name" not in st.session_state:
    st.session_state["model_name"] = model_name

# Check if the model has changed
if model_name != st.session_state["model_name"]:
    st.session_state["model_name"] = model_name

# Display the chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"]).write(msg["content"])
    else:
        st.chat_message(msg["role"]).write(f"({msg['model']}) {msg['content']}")

if prompt := st.chat_input("메시지를 입력하세요."):
    if not api_key:
        st.info("Please add your API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt, "model": "User"})
    st.chat_message("user").write(prompt)
    
    selected_model_info = model_info[model_name]
    client_type = selected_model_info["client"]
    
    if client_type == "OpenAI":
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=selected_model_info["model"],
            messages=st.session_state.messages
        )
        msg = response.choices[0].message.content
    elif client_type == "Gemini":
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(selected_model_info["model"])

        # Transform messages to the format expected by Gemini API
        gemini_messages = [{"role": "user" if msg["role"] == "user" else "model", "parts": [{"text": msg["content"]}]} for msg in st.session_state.messages]

        if "chat_session" not in st.session_state:    
            st.session_state["chat_session"] = model.start_chat(history=gemini_messages)

        chat_session = st.session_state["chat_session"]
        response = chat_session.send_message(prompt)
        msg = response.text

    st.session_state.messages.append({"role": "assistant", "content": msg, "model": model_name})
    st.chat_message("assistant").write(f"({model_name}) {msg}")
