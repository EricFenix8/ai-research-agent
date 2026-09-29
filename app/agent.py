from app.llm import LLM
from app.tools import TOOLS
import json

class Agent:

    def __init__(self, llm, tool_schemas):
        self.llm = llm
        self.tool_schemas = tool_schemas

    def execute_tool(self, tool_call):
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        
        tool_function = TOOLS.get(function_name)
        
        if tool_function is None:
            return f"Error: tool '{function_name}' not found."

        try:
            result = tool_function(**arguments)

        except Exception as error:
            return f"Error executing tool '{function_name}': {error}"

        return result

    def run(self, user_message, max_iterations = 5):

        messages = [
            {
                "role": "user",
                "content": user_message
            }
        ]

        iteration = 0
        
        while iteration < max_iterations:
            
            iteration += 1

            # Pregunta al LLM qué hacer
            response = self.llm.generate(
                messages,
                tools=self.tool_schemas
            )

            assistant_message = response["message"]
            print("\nLLM RESPONSE\n")
            print(assistant_message)

            messages.append(assistant_message)

            #Cuando ya no se necesite una herramienta se para
            if not assistant_message.get("tool_calls"):
                return assistant_message["content"]

            # Ejecuta cada herramienta requerida
            for tool_call in assistant_message["tool_calls"]:

                result = self.execute_tool(tool_call)
                print("\nTOOL RESULT")
                print(result)
                
                messages.append({
                    "role": "tool",
                    "tool_name": tool_call["function"]["name"],
                    "content": json.dumps(result, ensure_ascii=False)
                })
                
        return "reached the maximun iterations"