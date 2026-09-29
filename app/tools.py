def get_current_weather(city):
    return f"The weather in {city} is sunny."


weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city."
                }
            },
            "required": ["city"]
        }
    }
}


TOOLS = {
    "get_current_weather": get_current_weather
}