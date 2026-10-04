import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


FORBIDDEN_SECTION_MARKERS = (
    "references",
    "bibliography",
    "further reading",
    "external links",
    "see also",
    "notes",
    "citations",
    "sources",
    "works cited",
)


class Retriever:

    def __init__(self, chunk_size=500, top_k=3):
        self.chunk_size = chunk_size
        self.top_k = top_k

    def chunk_text(self, text):

        words = text.split()

        chunks = []

        overlap = 100

        step = self.chunk_size - overlap

        for i in range(0, len(words), step):

            chunk = " ".join(
                words[i:i + self.chunk_size]
            )

            if chunk:
                chunks.append(chunk)

        return chunks

    def _contains_forbidden_section(self, chunk):
        chunk_lower = re.sub(r"\s+", " ", chunk).lower()
        return any(marker in chunk_lower for marker in FORBIDDEN_SECTION_MARKERS)

    def retrieve(self, query, text):

        chunks = self.chunk_text(text)
        chunks = [chunk for chunk in chunks if not self._contains_forbidden_section(chunk)]

        if not chunks:
            return []

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        chunk_vectors = vectorizer.fit_transform(chunks)

        query_vector = vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            chunk_vectors
        )[0]

        ranked_chunks = sorted(
            zip(chunks, similarities),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "text": chunk,
                "score": float(score)
            }
            for chunk, score in ranked_chunks[:self.top_k]
        ]   