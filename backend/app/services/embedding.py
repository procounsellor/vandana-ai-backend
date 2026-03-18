from openai import OpenAI
from app.config import OPENAI_API_KEY

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a given text."""
    text = text.replace("\n", " ").strip()
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIM,
    )
    return response.data[0].embedding


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts in a single API call."""
    texts = [t.replace("\n", " ").strip() for t in texts]
    response = client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIM,
    )
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
