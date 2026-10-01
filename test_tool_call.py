from app.llm import LLM
from app.agent import Agent
from app.tools import wikipedia_tool, wikipedia_page_tool


llm = LLM()

agent = Agent(
    llm=llm,
    tool_schemas=[wikipedia_tool, wikipedia_page_tool]
)


answer = agent.run(
    "What is the detailed history of Alan Turing's work during World War II?"
)


print("\nFinal answer:")
print(answer)