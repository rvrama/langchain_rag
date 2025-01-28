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
from multipledispatch import dispatch 


model='gpt-3.5-turbo-instruct'
promptType = "rlm/rag-prompt"
vectorstore = InMemoryVectorStore
prompt = hub.pull(promptType)
llm = OpenAI(model = model)

@dispatch(str)
def init(_model):
    init(_model, promptType, vectorStore)

@dispatch(str, str)
def init(_model, _promptType):
    init(_model, _promptType, vectorstore)

@dispatch(str, str, object)
def init(_model, _promptType, _vectorStore):
    llm = _model #if model != "" else OpenAI(model='gpt-3.5-turbo-instruct')
    # Define prompt for question-answering
    prompt = hub.pull(_promptType) #if promptType != "" else hub.pull("rlm/rag-prompt")
    vectorstore = _vectorStore #if vectorStore else InMemoryVectorStore
    return True

def file_loader(filepath):
    file_path=filepath
    loader = PyPDFLoader(file_path)
    pages = []
    for page in loader.lazy_load():
        pages.append(page)
    return pages

def setUp(pages):
    vector_store = vectorstore.from_documents(pages, OpenAIEmbeddings())

    # Define state for application
    class State(TypedDict):
        question: str
        context: List[Document]
        answer: str

    # Define application steps
    # internal method
    def _retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}

    #internal method
    def _generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response}

    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([_retrieve, _generate])
    graph_builder.add_edge(START, "_retrieve")
    graph = graph_builder.compile()
    return graph

def getResults(graph, question):
    response = graph.invoke({"question": question})
    return response["answer"]

