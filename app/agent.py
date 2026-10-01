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

        system_prompt = """
        You are a research assistant.

        Your goal is to provide accurate answers based on information
        retrieved from available tools.

        When answering factual questions:

        1. Use search tools to find relevant sources.
        2. After finding a relevant source, retrieve its detailed content
        using the appropriate tool before answering.
        3. Base your final answer on the retrieved information.
        4. Do not invent facts that are not supported by the retrieved sources.
        5. Do not ask the user whether you should retrieve a source.
        If retrieving the source is useful, do it yourself.
        """
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role":"user",
                "content":user_message
            }
        ]

        iteration = 0
        
        while iteration < max_iterations:
            
            iteration += 1

            print("\n========== MESSAGES ==========")


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
                print("\nTOOL:", tool_call["function"]["name"])

                if isinstance(result, dict):
                    print("TITLE:", result.get("title"))
                    print("URL:", result.get("url"))
                    print("CONTENT LENGTH:", len(result.get("content", "")))
                print("\nTOOL RESULT")
                
                messages.append({
                    "role": "tool",
                    "tool_name": tool_call["function"]["name"],
                    "content": json.dumps(result, ensure_ascii=False)
                })
                
        return "reached the maximun iterations"