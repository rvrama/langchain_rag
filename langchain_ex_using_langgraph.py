import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

from langchain_community.vectorstores import FAISS, InMemoryVectorStore
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import env

llm = OpenAI(model='gpt-3.5-turbo-instruct')

file_path=".\documents\dotnet_microservices.pdf"
print("File path " + file_path)
loader = PyPDFLoader(file_path)
pages = []
for page in loader.lazy_load():
    pages.append(page)

vector_store = InMemoryVectorStore.from_documents(pages, OpenAIEmbeddings())

# # Load and chunk contents of the blog
# loader = WebBaseLoader(
#       web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             class_=("post-content", "post-title", "post-header")
#         )
#     ),
# )
# docs = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# all_splits = text_splitter.split_documents(docs)

# vector_store = InMemoryVectorStore.from_documents([], OpenAIEmbeddings())
  
# # Index chunks
# _ = vector_store.add_documents(documents=all_splits)



# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

while (True):
    question = input("Ask a question: ")
    if question == "exit":
        break
    response = graph.invoke({"question": question})
    print(f'\n\n Answer : " {response["answer"]} \n\n')

