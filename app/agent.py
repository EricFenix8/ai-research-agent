from app.llm import LLM
from app.tools import TOOLS
from app.retriever import Retriever
import json


class Agent:

    def __init__(self, llm, tool_schemas):
        self.llm = llm
        self.tool_schemas = tool_schemas
        self.retriever = Retriever(chunk_size=500, top_k=3)

    def _attach_relevant_context(self, tool_name, result, query):
        if tool_name != "get_wikipedia_page":
            return result

        if not isinstance(result, dict) or "content" not in result:
            return result

        page_text = result["content"]
        if not page_text:
            return result

        relevant_chunks = self.retriever.retrieve(query, page_text)
        if not relevant_chunks:
            return result

        focused_content = "\n\n".join(chunk["text"] for chunk in relevant_chunks)
        result["content"] = focused_content
        result["retrieved_chunks"] = relevant_chunks
        return result

    def execute_tool(self, tool_call, query=None):
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        
        tool_function = TOOLS.get(function_name)
        
        if tool_function is None:
            return f"Error: tool '{function_name}' not found."

        try:
            result = tool_function(**arguments)

        except Exception as error:
            return f"Error executing tool '{function_name}': {error}"

        return self._attach_relevant_context(function_name, result, query)

    def run(self, user_message, max_iterations = 5):

        system_prompt = """
        You are a research assistant.

        Your goal is to provide accurate answers based on information
        retrieved from available tools.

        When answering factual questions:

        1. Use search tools to find relevant sources.
        2. After finding a relevant source, retrieve its detailed content
        using the appropriate tool before answering.
        3. Prefer the canonical article page that matches the topic exactly.
           Do not choose book, biography, film, or subtitle pages when the
           main article page is available.
        4. Base your final answer on the retrieved information.
        5. Do not invent facts that are not supported by the retrieved sources.
        6. Do not ask the user whether you should retrieve a source.
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

                tool_name = tool_call["function"]["name"]
                result = self.execute_tool(tool_call, query=user_message)
                print("\nTOOL:", tool_name)

                if isinstance(result, dict):
                    print("TITLE:", result.get("title"))
                    print("URL:", result.get("url"))
                    print("CONTENT LENGTH:", len(result.get("content", "")))
                    if "retrieved_chunks" in result:
                        print("RELEVANT CHUNKS:", len(result["retrieved_chunks"]))
                
                messages.append({
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
                
        return "reached the maximun iterations"