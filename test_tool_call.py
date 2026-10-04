from app.llm import LLM
from app.agent import Agent
from app.tools import calculator_tool, wikipedia_tool, wikipedia_page_tool


llm = LLM()

agent = Agent(
    llm=llm,
    tool_schemas=[calculator_tool, wikipedia_tool, wikipedia_page_tool]
)


answer = agent.run(
    "2+2"
)


print("\nFinal answer:")
print(answer)