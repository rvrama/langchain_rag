from dotenv import load_dotenv
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.schema import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")
# Initialize the LLM (Replace 'your-openai-api-key' with your actual API key)
llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=open_api_key)

# set the LANGSMITH_API_KEY environment variable (create key in settings)
prompt = hub.pull("rvwaran/multichoice_quiz")

# Set up memory to retain conversation history
memory = ConversationBufferMemory()  

promptmessage = prompt.invoke({"options_count":4, 
                            "points_per_question":10, 
                            "num_of_questions":5, 
                            "topic": "Azure Containers"
                            })

conversation = ConversationChain(llm=llm, memory=memory)
response = conversation.run({"input": promptmessage.messages[0].content})

question = response

print("\n ChatBot: Hello! Type 'exit' to end the conversation.\n")

# Add user input to memory and get AI's response with context
#memory.save_context({"input": question}, {"output": ""})  # Saving user input

# Interactive chat loop
while True:
    user_input = input("You: ").strip()  # Get user input
    
    if user_input.lower() == "exit":
        print("ChatBot: Goodbye!")
        break  # Exit loop if user types 'exit'

    response = conversation.run({"input":user_input})

    bot_response = response

    print(f" ChatBot: {bot_response}")  # Print bot response
