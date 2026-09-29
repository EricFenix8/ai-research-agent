from app.llm import LLM
from app.tools import TOOLS


class Agent:

    def __init__(self, llm, tool_schemas):
        self.llm = llm
        self.tool_schemas = tool_schemas

    def run(self, user_message):

        messages = [
            {
                "role": "user",
                "content": user_message
            }
        ]

        while True:

            # Ask the LLM what to do
            response = self.llm.generate(
                messages,
                tools=self.tool_schemas
            )

            assistant_message = response["message"]

            messages.append(assistant_message)

            # If the LLM does not request a tool,
            # the answer is complete
            if not assistant_message.get("tool_calls"):
                return assistant_message["content"]

            # Execute every requested tool
            for tool_call in assistant_message["tool_calls"]:

                function_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]

                tool_function = TOOLS[function_name]

                result = tool_function(
                    **arguments
                )

                messages.append({
                    "role": "tool",
                    "tool_name": function_name,
                    "content": result
                })