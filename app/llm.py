from ollama import chat


class LLM:

    def __init__(self, model_name="qwen2.5:3b"):
        self.model_name = model_name

    def generate(self, messages, tools=None):

        response = chat(
            model=self.model_name,
            messages=messages,
            tools=tools
        )

        return response