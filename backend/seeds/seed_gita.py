"""
Seed script for Bhagavad Gita verses.
Data source: https://github.com/gita/gita (The Unlicense / Public Domain)

Run from the backend/ directory:
    python -m seeds.seed_gita
"""
import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import Scripture, Verse, VerseTranslation

DATA_DIR = Path(__file__).parent / "data"

# Authors to seed (author_id from translation.json)
# Add more as needed
ENGLISH_AUTHORS = {
    16: "Swami Sivananda",
    18: "Swami Adidevananda",
}


def load_data():
    verses = json.loads((DATA_DIR / "verse.json").read_text())
    translations = json.loads((DATA_DIR / "translation.json").read_text())

    # Skip the duplicate verse (dataset has 701 entries, one is a duplicate)
    seen = set()
    unique_verses = []
    for v in verses:
        key = (v["chapter_number"], v["verse_number"])
        if key not in seen:
            seen.add(key)
            unique_verses.append(v)

    # Index translations by verse_id and author_id
    translation_map: dict[tuple, str] = {}
    for t in translations:
        if t["lang"] == "english" and t["author_id"] in ENGLISH_AUTHORS:
            translation_map[(t["verse_id"], t["author_id"])] = t["description"].strip()

    return unique_verses, translation_map


def seed(db: Session):
    # Check if already seeded
    existing = db.query(Scripture).filter_by(short_name="gita").first()
    if existing:
        print("Bhagavad Gita already seeded. Skipping.")
        return

    print("Creating Scripture record...")
    scripture = Scripture(
        name="Bhagavad Gita",
        short_name="gita",
        description=(
            "The Bhagavad Gita is a 700-verse Hindu scripture that is part of "
            "the epic Mahabharata. It presents a dialogue between Prince Arjuna "
            "and the god Krishna on the battlefield of Kurukshetra."
        ),
        language="Sanskrit",
    )
    db.add(scripture)
    db.flush()  # Get scripture.id before inserting verses

    verses_data, translation_map = load_data()
    print(f"Seeding {len(verses_data)} verses...")

    for i, v in enumerate(verses_data):
        verse = Verse(
            scripture_id=scripture.id,
            chapter=v["chapter_number"],
            verse_number=str(v["verse_number"]),
            sanskrit=v["text"].strip(),
            transliteration=v["transliteration"].strip(),
        )
        db.add(verse)
        db.flush()  # Get verse.id before inserting translations

        # Add English translations from selected authors
        for author_id, author_name in ENGLISH_AUTHORS.items():
            text = translation_map.get((v["id"], author_id))
            if text:
                db.add(VerseTranslation(
                    verse_id=verse.id,
                    language_code="en",
                    author=author_name,
                    translation=text,
                ))

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(verses_data)} verses inserted...")

    db.commit()
    print(f"Done! Seeded {len(verses_data)} verses with translations.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()
