import requests
from bs4 import BeautifulSoup


def get_current_weather(city):
    return f"The weather in {city} is sunny."

def search_wikipedia(query):

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 5
    }

    response = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "AIResearchAgent project"
       },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for result in data["query"]["search"]:

        snippet = BeautifulSoup(
            result["snippet"],
            "html.parser"
        ).get_text(" ", strip=True)

        results.append({
            "title": result["title"],
            "snippet": snippet,
            "url": (
                "https://en.wikipedia.org/wiki/"
                + result["title"].replace(" ", "_")
            )
        })

    return results


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

wikipedia_tool = {
    "type": "function",
    "function": {
        "name": "search_wikipedia",
        "description": "Search Wikipedia for information about a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The topic to search for on Wikipedia."
                }
            },
            "required": ["query"]
        }
    }
}


TOOLS = {
    "get_current_weather": get_current_weather,
    "search_wikipedia": search_wikipedia

}