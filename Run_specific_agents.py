from agents import Agent, ModelSettings, Runner
import asyncio
import env


history_teacher = Agent(
    name="History_Teacher",
    model="gpt-4o",
    instructions="You are a helpful AI assistant which provides the answers ONLY to the history questions",
)

math_teacher = Agent(
    name="Maths_Teacher",
    model="gpt-4o",
    instructions="You are a helpful AI assistant which provides the answers ONLY to the maths questions",
)

teacher = Agent(
    name="Teacher",
    model="gpt-4o",
    instructions="You are a helpful AI assistant which provides the answers to the questions on history or Math by handing off to the respective teacher."
      "In case of other subjects, throw an appropriate error message",
    handoffs=[history_teacher, math_teacher]
)

async def main():
    while True:
        query = input("Enter your question on history or math for AI to answer(type 'exit' to quit) : ")
        if query.lower() == "exit":
            break
        result = await Runner.run(teacher, query)
        print(result.final_output)
        print("\n\n")


if __name__ == "__main__":
  asyncio.run(main())
