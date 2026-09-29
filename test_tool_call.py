from app.llm import LLM
from app.agent import Agent
from app.tools import weather_tool


llm = LLM()

agent = Agent(
    llm=llm,
    tool_schemas=[weather_tool]
)


answer = agent.run(
    "What is the weather like in Madrid?"
)


print("\nFinal answer:")
print(answer)