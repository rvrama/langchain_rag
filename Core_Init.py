import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS, InMemoryVectorStore
from langchain_openai import OpenAI, OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os
from multipledispatch import dispatch 

load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")
langsmith_key = os.getenv("LANGSMITH_API_KEY")
os.environ["OPENAI_API_KEY"] = open_api_key
os.environ["LANGSMITH_API_KEY"] = langsmith_key

model='gpt-3.5-turbo'
promptType = "rlm/rag-prompt"
vectorstore = FAISS #InMemoryVectorStore
prompt = hub.pull(promptType)
llm = ChatOpenAI(model = model)

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002") #"text-embedding-3-small")
VECTORSTORE_DIR = 'faiss_index'

@dispatch(str)
def init(_model):
    init(_model, promptType, '', vectorStore) #promptType and promptText are defined internally

@dispatch(str, str, str)
def init(_model, _promptType, _promptText):
    init(_model, _promptType, _promptText, vectorstore) #promptType is given as 'Text' and promptText is provided as string or promptType is not provided or given as hub prompt (like rlm/rag-prompt and prompttext is given empty)

@dispatch(str, str, str, object)
def init(_model, _promptType, _promptText, _vectorStore):
    llm = OpenAI(model=_model) #if model != "" else OpenAI(model='gpt-3.5-turbo-instruct')
    # Define prompt for question-answering
    if (_promptType!='Text'):
        prompt = hub.pull(_promptType)
    else:
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=_promptText)

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
      # If vectorstore already exists, load it
    if os.path.exists(VECTORSTORE_DIR):
        print("Loading vectorstore from disk...")
        vector_store = FAISS.load_local(VECTORSTORE_DIR, embeddings, allow_dangerous_deserialization=True)
    else:
        print("Creating new vectorstore from documents...")
        # Step 1: Chunk documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=25)
        docs = text_splitter.split_documents(pages)

        # Step 2: Create vector store from chunks
        vector_store = vectorstore.from_documents(docs, embeddings)

        # Save to disk
        vector_store.save_local(VECTORSTORE_DIR)

    # Define state for application
    class State(TypedDict):
        question: str
        context: List[Document]
        answer: str

    # Define application steps
    # internal method
    def _retrieve(state: State):
        docs_with_scores = vector_store.similarity_search_with_score(
        query=state["question"], k=4
        )
        
        RELEVANCE_THRESHOLD = 0.4  # Tweak as needed
        
        filtered_docs = [
        doc for doc, score in docs_with_scores if score <= RELEVANCE_THRESHOLD
        ]

        if not filtered_docs:
        # Inject a fake doc with a polite message so _generate can still run
            return {
            "context": [
                Document(page_content="No relevant documents found for the question.")
            ]
        }
       
        return {"context": filtered_docs}

    #internal method
    def _generate(state: State):
        if "No relevant documents found" in state["context"][0].page_content:
            return {"answer": "I couldn’t find anything relevant in the documents I have."}
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)

        return {"answer": response.content}

    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([_retrieve, _generate])
    graph_builder.add_edge(START, "_retrieve")
    graph = graph_builder.compile()
    return graph

def getResults(graph, question): 
    response = graph.invoke({"question": question})
    return response["answer"]

