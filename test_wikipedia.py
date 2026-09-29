from app.tools import search_wikipedia


results = search_wikipedia("Alan Turing")


for result in results:

    print("\nTitle:", result["title"])
    print("URL:", result["url"])
    print("Snippet:", result["snippet"])