from app.retriever import Retriever
from app.tools import get_wikipedia_page


retriever = Retriever(
    chunk_size=500,
    top_k=3
)

page = get_wikipedia_page("Alan Turing")

results = retriever.retrieve(
    query="How did Alan Turing contribute to breaking Enigma?",
    text=page["content"]
)

for i, result in enumerate(results, start=1):

    print(f"\n--- RESULT {i} ---")
    print("Score:", result["score"])
    print("Text:")
    print(result["text"])