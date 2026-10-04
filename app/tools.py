import ast
import re

import requests
from bs4 import BeautifulSoup


ALLOWED_NODES = {
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Constant,
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
}


NON_ARTICLE_TITLE_TOKENS = {
    "book", "books", "film", "films", "movie", "movies", "biography",
    "biographies", "novel", "novels", "play", "plays", "album",
    "albums", "song", "songs", "episode", "episodes", "series",
    "guide", "manual", "documentary", "documentaries", "tv",
    "theatre", "theater"
}


def _normalize_tokens(value):
    return [token for token in re.split(r"[^a-z0-9]+", (value or "").lower()) if token]


def _wikipedia_result_priority(query, title):
    q = (query or "").strip()
    t = (title or "").strip()

    if not q or not t:
        return -10_000

    q_tokens = _normalize_tokens(q)
    t_tokens = _normalize_tokens(t)
    main_title = t.split(":", 1)[0].strip()
    main_tokens = _normalize_tokens(main_title)

    score = 0

    if t.lower() == q.lower():
        score += 600
    elif t.lower().startswith(q.lower()):
        score += 350
    elif q.lower().startswith(t.lower()):
        score += 250
    elif q.lower() in t.lower():
        score += 200

    overlap = sum(1 for token in q_tokens if token in t_tokens)
    score += overlap * 80

    main_overlap = sum(1 for token in q_tokens if token in main_tokens)
    score += main_overlap * 60

    if ":" in t:
        # Subtitle pages are often books, biographies or related works, not the main article.
        score -= 200 if main_overlap < max(2, len(q_tokens)) else 50

    if any(token in t_tokens for token in NON_ARTICLE_TITLE_TOKENS):
        score -= 300

    if "by " in t.lower() and main_overlap < len(q_tokens):
        score -= 150

    if main_tokens and main_tokens[0] in q_tokens:
        score += 50

    return score


FORBIDDEN_WIKIPEDIA_TITLES = {
    "references",
    "bibliography",
    "further reading",
    "external links",
    "see also",
    "notes",
    "citations",
    "sources",
    "works cited",
    "references and notes",
    "notes and references",
    "further reading and external links",
}


def _clean_wikipedia_text(text):
    cleaned = re.sub(r"\s+", " ", text).strip()
    lower = cleaned.lower()

    for marker in sorted(FORBIDDEN_WIKIPEDIA_TITLES, key=len, reverse=True):
        pattern = rf"\b{re.escape(marker)}\b\s*(?:\[ edit \])?"
        match = re.search(pattern, lower)
        if match:
            cleaned = cleaned[:match.start()].strip()
            break

    return cleaned


def get_current_weather(city):
    return f"The weather in {city} is sunny."


def calculate(expression):
    if not isinstance(expression, str):
        raise ValueError("expression must be a string")

    cleaned = expression.strip()
    if not cleaned:
        raise ValueError("expression cannot be empty")

    try:
        parsed = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression: {exc.msg}") from exc

    for node in ast.walk(parsed):
        if not isinstance(node, tuple(ALLOWED_NODES)):
            raise ValueError(f"Unsupported expression: {type(node).__name__}")

    def _eval(node):
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants are allowed")
            return node.value

        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left ** right
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")

        if isinstance(node, ast.UnaryOp):
            value = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.USub):
                return -value
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")

        if isinstance(node, ast.Expression):
            return _eval(node.body)

        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

    result = _eval(parsed)
    return {
        "expression": cleaned,
        "result": result,
    }


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
            ),
            "_priority": _wikipedia_result_priority(query, result["title"])
        })

    results.sort(key=lambda item: item["_priority"], reverse=True)

    for result in results:
        result.pop("_priority", None)

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

    # Remove sections that are not part of the main article content
    for element in soup.select(
        ".mw-references-wrap, .reflist, .navbox, .vertical-navbox, "
        ".metadata, .ambox, .hatnote, .toc, table, sup.reference, "
        "div#toc, div.thumb, div.floatright, div.floatleft, .mw-editsection"
    ):
        element.decompose()

    text = soup.get_text(" ", strip=True)
    text = _clean_wikipedia_text(text)

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

calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Safely evaluate a numeric expression using arithmetic operators.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression such as 2 + 3 * 4 or (10 / 2) + 5."
                }
            },
            "required": ["expression"]
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
    "calculate": calculate,
    "search_wikipedia": search_wikipedia,
    "get_wikipedia_page": get_wikipedia_page

}