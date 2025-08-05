from openai import OpenAI
import streamlit as st
import Core_Init
import os

open_api_key = os.getenv("OPENAI_API_KEY")
promptText = """
You are an assistant to help in answering ONLY related to pets. Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Do not provide any answers that are not relevant to the retrieved context or user question if the question is not related to pet handling or pet care.

Context:
{context}

Question:
{question}

Answer:
"""

# entried in .env
#OPENAI_API_KEY = "sk-proj-..."
#LANGSMITH_API_KEY = "lsv2_..."

if "init" not in st.session_state:
    st.session_state["init"] = Core_Init.init('gpt-3.5-turbo', 'Text', promptText)

if "pages" not in st.session_state:
    st.session_state["pages"] = Core_Init.file_loader(".\\documents\\petcare.pdf")

if "graph" not in st.session_state:
    st.session_state["graph"] = Core_Init.setUp(st.session_state["pages"])

st.title("Ask me about your pets!!")

#client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# client = OpenAI()

# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
#    with st.chat_message("user"):
#        st.markdown(prompt)

#prompt = prompt if prompt else "Tell me about you"
if prompt:
    response = Core_Init.getResults( st.session_state["graph"], prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

for message in st.session_state.messages:
   with st.chat_message(message["role"]):
    st.markdown(message["content"])

