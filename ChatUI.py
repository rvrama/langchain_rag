from openai import OpenAI
import streamlit as st
import Core_Init
import env

if "init" not in st.session_state:
    st.session_state["init"] = Core_Init.init('gpt-3.5-turbo-instruct', 'rlm/rag-prompt')

if "pages" not in st.session_state:
    st.session_state["pages"] = Core_Init.file_loader(".\documents\dotnet.pdf")

if "graph" not in st.session_state:
    st.session_state["graph"] = Core_Init.setUp(st.session_state["pages"])

st.title("Get your answers from the AI")

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

