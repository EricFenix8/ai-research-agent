from app.llm import LLM
from app.agent import Agent
from app.tools import wikipedia_tool


llm = LLM()

agent = Agent(
    llm=llm,
    tool_schemas=[wikipedia_tool]
)


answer = agent.run(
    "Who was Alan Turing?"
)


print("\nFinal answer:")
print(answer)