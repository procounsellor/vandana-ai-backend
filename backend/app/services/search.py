from sqlalchemy.orm import Session, joinedload
from pgvector.sqlalchemy import Vector
from sqlalchemy import select

from app.models import Verse
from app.services.embedding import get_embedding


def search_verses(query: str, db: Session, language_code: str = "en", top_k: int = 5) -> list[Verse]:
    """Find the most semantically relevant verses for a user query."""
    query_embedding = get_embedding(query)

    results = (
        db.query(Verse)
        .options(joinedload(Verse.translations), joinedload(Verse.scripture))
        .filter(Verse.embedding.isnot(None))
        .order_by(Verse.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    return results
