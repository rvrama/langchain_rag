from openai import OpenAI
import streamlit as st
import Core_Init
import os


st.set_page_config( initial_sidebar_state="collapsed")

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
st.page_link("Home.py", label="<- Home")

st.title("Book a Sitter")
st.write("Ask me about pets?")
st.markdown("You can ask me about pets, pet care, pet handling, etc.")
