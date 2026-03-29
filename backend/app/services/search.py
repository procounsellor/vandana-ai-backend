from sqlalchemy.orm import Session, joinedload

from app.models import Verse, Scripture
from app.services.embedding import get_embedding


def search_verses(
    query: str,
    db: Session,
    language_code: str = "en",
    top_k: int = 5,
    scripture_short_names: list[str] | None = None,
) -> list[Verse]:
    """Find the most semantically relevant verses for a user query."""
    query_embedding = get_embedding(query)
    return search_verses_by_embedding(query_embedding, db, top_k=top_k, scripture_short_names=scripture_short_names)


def search_verses_by_embedding(
    embedding: list[float],
    db: Session,
    top_k: int = 5,
    scripture_short_names: list[str] | None = None,
) -> list[Verse]:
    """Find the most semantically relevant verses using a precomputed embedding."""
    q = (
        db.query(Verse)
        .options(joinedload(Verse.translations), joinedload(Verse.scripture))
        .filter(Verse.embedding.isnot(None))
    )
    if scripture_short_names:
        q = q.join(Scripture).filter(Scripture.short_name.in_(scripture_short_names))
    return q.order_by(Verse.embedding.cosine_distance(embedding)).limit(top_k).all()
