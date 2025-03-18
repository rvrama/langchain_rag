from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_community.utilities import SerpAPIWrapper
import asyncio
import env


history_teacher = AssistantAgent(
    name="History_Teacher",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You are a helpful AI assistant which provides the answers ONLY to the history questions",
)

math_teacher = AssistantAgent(
    name="Maths_Teacher",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="You are a helpful AI assistant which provides the answers ONLY to the maths questions",
)

teacher = AssistantAgent(
    name="Teacher",
    model_client=OpenAIChatCompletionClient(model="gpt-4o"),
    system_message="""You are a helpful AI assistant which delegate the tasks to other agents as follows
       1. history_teacher : Will answer all history questions
       2. math_teacher : Will answer all Mathematics questions
       
       In case of other subjects, throw an appropriate error message saying "You are NOT trained to answer any questions other than History or Math.".
      After all tasks are done, summarize the findings and end with "TERMINATE" to end the conversation.
      """,
)

termination = TextMentionTermination("TERMINATE")

team = SelectorGroupChat([teacher, history_teacher, math_teacher], 
                        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
                        termination_condition=termination)

async def main():
    while True:
        query = input("Ask your question on History or Math (type 'exit' to quit) : ")
        if query.lower() == "exit":
            break
        stream = team.run_stream(task=query)
        await Console(stream)

if __name__ == "__main__":
  asyncio.run(main())

