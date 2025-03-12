from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_community.utilities import SerpAPIWrapper
import asyncio
import env
## make sure env file contains os.environ["OPENAI_API_KEY"] and os.environ["SERPAPI_API_KEY"]

def get_glassdoor_rating(query: str):
    search = SerpAPIWrapper()
    result = search.run(f"{query} Glassdoor rating")
    return (result)

glassdoor_rating_tool = FunctionTool(
    get_glassdoor_rating, description="Search Google for information, returns results with a snippet and body content"
)

planning_agent = AssistantAgent( 
    name="Planning_Agent",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="""You are a planning agent. 
    Your job is to break the tasks into smaller, manageable subtasks.
    Your team members are :
    Company_researcher : Summarizes about the company
    Finance_analyst : Reports the current finance status of the company
    Review_analyst : Reports the glassdoor review of the company.  Only the review ratings.
    
    You have to plan and delegate the tasks - you do not execute them yourself.

    When assigning tasks use the following format:
    1. <Agent> : <task>

    After all tasks are done, summarize the findings and end with "TERMINATE" to end the conversation.

    """

)

company_researcher = AssistantAgent( 
    name="Company_Researcher",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You are a helpful AI assistant which will summarize about the company in less than 100 words"
)

finance_analyst = AssistantAgent(
    name="Finance_Analyst",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You are a helpful AI assistant which provides the finance status of the company. Provide Revenue, Profit and quick Financial report",
)

review_analyst = AssistantAgent(
    name="Review_Analyst",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    tools=[glassdoor_rating_tool],
    system_message="You are a helpful AI assistant which retrieves the glassdoor ratings of the company",
)

termination = TextMentionTermination("TERMINIATE") | MaxMessageTermination(max_messages=10)

team = SelectorGroupChat([planning_agent, company_researcher, finance_analyst, review_analyst], 
                        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
                        termination_condition=termination)

async def main():
    while True:
        query = input("Enter company name to research (type 'exit' to quit) : ")
        if query.lower() == "exit":
            break
        print(query)
        task = "Write about the company " + query
        stream = team.run_stream(task=task)
        await Console(stream)

if __name__ == "__main__":
  asyncio.run(main())
