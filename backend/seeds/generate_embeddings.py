"""
Generate and store embeddings for all verses in the database.
Embeds the English translation (Swami Sivananda) for each verse.

Run from the backend/ directory:
    python -m seeds.generate_embeddings
"""
import sys
import time

from sqlalchemy.orm import Session, joinedload

from app.db import SessionLocal
from app.models import Verse
from app.services.embedding import get_embeddings_batch

BATCH_SIZE = 100  # OpenAI allows up to 2048 inputs per request
AUTHOR = "Swami Sivananda"


def get_verse_text(verse: Verse) -> str:
    """Build the text to embed for a verse."""
    parts = []

    # Include translation for semantic meaning
    for t in verse.translations:
        if t.author == AUTHOR and t.language_code == "en":
            parts.append(t.translation)
            break

    # Include transliteration for phonetic context
    if verse.transliteration:
        parts.append(verse.transliteration)

    return " ".join(parts)


def generate_embeddings(db: Session):
    verses = (
        db.query(Verse)
        .options(joinedload(Verse.translations))
        .filter(Verse.embedding == None)  # noqa: E711 — only process un-embedded verses
        .all()
    )

    if not verses:
        print("All verses already have embeddings.")
        return

    print(f"Generating embeddings for {len(verses)} verses in batches of {BATCH_SIZE}...")

    for i in range(0, len(verses), BATCH_SIZE):
        batch = verses[i:i + BATCH_SIZE]
        texts = [get_verse_text(v) for v in batch]

        embeddings = get_embeddings_batch(texts)

        for verse, embedding in zip(batch, embeddings):
            verse.embedding = embedding

        db.commit()
        print(f"  {min(i + BATCH_SIZE, len(verses))}/{len(verses)} verses embedded...")

        # Avoid hitting rate limits
        if i + BATCH_SIZE < len(verses):
            time.sleep(0.5)

    print("Done! All verses now have embeddings.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        generate_embeddings(db)
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()
