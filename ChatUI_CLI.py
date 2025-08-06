from openai import OpenAI
import Core_Init
import os

open_api_key = os.getenv("OPENAI_API_KEY")
promptText = """
System : You are an assistant to help in answering ONLY related to pets. Use the following pieces of retrieved context to answer the question. 
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

Core_Init.init('gpt-3.5-turbo', 'Text', promptText)

pages = Core_Init.file_loader(".\\documents\\petcare.pdf")

graph = Core_Init.setUp(pages)

while (True):
    question = input("Enter your question ('exit' to quit): ")
    if question == "exit":
        break
    response = Core_Init.getResults(graph, question)
    print(response)



