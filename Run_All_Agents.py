from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_community.utilities import SerpAPIWrapper
from agents import Agent, ModelSettings, function_tool, Runner
import asyncio
import env

@function_tool
def get_glassdoor_rating(query: str):
    search = SerpAPIWrapper()
    result = search.run(f"{query} Glassdoor rating")
    return (result)

@function_tool
def get_director_info(query: str):
    search = SerpAPIWrapper()
    result = search.run(f"{query} director information site:zaubacorp.com")
    return (result)



finance_analyst = Agent(
    name="Finance_Analyst",
    model="gpt-4o",
    instructions="You are a helpful AI assistant which provides the finance status of the company. Provide Revenue, Profit and quick Financial report",
)

director_info = Agent(
    name="Director_Info",
    model="gpt-4o",
    tools=[get_director_info],  ##  this tool will fetch the director details from Zaubacorp which works only for Indian companies
    instructions="You are a helpful AI assistant which retrieves the Director's information of the company from Zaubacorp website"
)

review_analyst = Agent(
    name="Review_Analyst",
    model="gpt-4o",
    tools=[get_glassdoor_rating],
    instructions="You are a helpful AI assistant which retrieves the glassdoor ratings of the company",
)

company_researcher = Agent( 
    name="Company_Researcher",
    model="gpt-4o",
    instructions="You are a helpful AI assistant which will summarize about the company in less than 100 words",

)

async def main():
    while True:
        query = input("Enter company name to research (type 'exit' to quit) : ")
        if query.lower() == "exit":
            break
        print(query)
        taskDesc = "Write about the company " + query
        result = await Runner.run(company_researcher, taskDesc)
        print(result.final_output)
        print("\n\n\n")

        result = await Runner.run(finance_analyst, taskDesc)
        print(result.final_output)
        print("\n\n\n")

        result = await Runner.run(review_analyst, taskDesc)
        print(result.final_output)
        print("\n\n\n")

        result = await Runner.run(director_info, taskDesc)
        print(result.final_output)
        print("\n\n\n")

        ## The above repetitive code can be simplified by using asyncio.gather()

if __name__ == "__main__":
  asyncio.run(main())
