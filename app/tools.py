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

def get_wikipedia_page(title):
    url = "https://en.wikipedia.org/w/api.php"

    print("He llegado a wikipage")
    
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "redirects": True
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

    html = data["parse"]["text"]["*"]

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(" ", strip=True)

    return {
        "title": data["parse"]["title"],
        "url": (
            "https://en.wikipedia.org/wiki/"
            + data["parse"]["title"].replace(" ", "_")
        ),
        "content": text
    }

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
        "description": ("Search Wikipedia to find relevant articles about a topic. "
            "Use this tool when you need to discover relevant Wikipedia pages. "
            "After finding a relevant page, use get_wikipedia_page to retrieve "
            "its detailed content before answering."),
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

wikipedia_page_tool = {
    "type": "function",
    "function": {
        "name": "get_wikipedia_page",
        "description": ("Retrieve the detailed content of a specific Wikipedia page. "
            "Use this after search_wikipedia when you need reliable and "
            "detailed information from the selected article."),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The exact title of the Wikipedia page to retrieve."
                }
            },
            "required": ["title"]
        }
    }
}

TOOLS = {
    "get_current_weather": get_current_weather,
    "search_wikipedia": search_wikipedia,
    "get_wikipedia_page": get_wikipedia_page

}