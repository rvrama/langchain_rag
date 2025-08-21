from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langgraph.graph import StateGraph
import env

# Initialize OpenAI LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Function to fetch company summary and update state
def get_company_summary(state):
    search = SerpAPIWrapper()
    result = search.run(f"{state['query']} company profile")
    return {**state, "company_summary": result}

# Function to fetch financial report and update state
def get_financial_report(state):
    search = SerpAPIWrapper()
    result = search.run(f"{state['query']} revenue and financial report")
    return {**state, "financial_report": result}

# Function to fetch Glassdoor rating and update state
def get_glassdoor_rating(state):
    search = SerpAPIWrapper()
    result = search.run(f"{state['query']} Glassdoor rating")
    return {**state, "glassdoor_rating": result}

# Define LangGraph
graph = StateGraph(dict)  # Ensure dictionary-based state

# Add Nodes
graph.add_node("get_summary", get_company_summary)
graph.add_node("get_financial", get_financial_report)
graph.add_node("get_glassdoor", get_glassdoor_rating)

# Define edges (workflow)
graph.set_entry_point("get_summary")
graph.add_edge("get_summary", "get_financial")
graph.add_edge("get_financial", "get_glassdoor")
graph.set_finish_point("get_glassdoor")

# Compile the graph
executable = graph.compile()

# Run the workflow
while True:
    company_name = input("Enter company name: ")
    if company_name.lower() == "exit":
        break
    result = executable.invoke({"query": company_name})
    print("\n\n Company Summary:", result.get("company_summary")[:300])
    print("\n\n Financial Report:", result.get("financial_report")[:300])
    print("\n\n Glassdoor Rating:", result.get("glassdoor_rating")[:300])
