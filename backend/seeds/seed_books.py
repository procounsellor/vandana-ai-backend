"""
Seed script for all non-Gita scriptures.
Run from the backend/ directory:
    python -m seeds.seed_books
"""
import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Scripture, Verse, VerseTranslation

DATA_DIR = Path(__file__).parent / "data"

BOOKS = [
    {
        "short_name": "yoga_sutras",
        "name": "Yoga Sutras of Patanjali",
        "description": "The Yoga Sutras of Patanjali are 196 aphorisms that form the foundational text of Raja Yoga. Composed around 400 CE, they outline the eight-limbed path to liberation and the nature of the mind.",
        "language": "Sanskrit",
        "file": "yoga_sutras.json",
    },
    {
        "short_name": "chanakya_neeti",
        "name": "Chanakya Neeti",
        "description": "Chanakya Neeti is a collection of aphorisms by the ancient Indian philosopher and statesman Chanakya (Kautilya), covering practical wisdom on ethics, politics, economics, and everyday life.",
        "language": "Sanskrit",
        "file": "chanakya_neeti.json",
    },
    {
        "short_name": "arthashastra",
        "name": "Arthashastra",
        "description": "The Arthashastra is an ancient Indian treatise on statecraft, economic policy, and military strategy, written by Chanakya (Kautilya) around the 3rd century BCE.",
        "language": "Sanskrit",
        "file": "arthashastra.json",
    },
    {
        "short_name": "kama_sutra",
        "name": "Kama Sutra",
        "description": "The Kama Sutra by Vatsyayana is an ancient Indian text on the nature of love, family life, and social conduct. It is far more than its modern reputation — a guide to the art of living well.",
        "language": "Sanskrit",
        "file": "kama_sutra.json",
    },
    {
        "short_name": "upanishads",
        "name": "Upanishads",
        "description": "The Upanishads are a collection of ancient Sanskrit texts that contain the earliest emergence of some of the central religious concepts of Hinduism, Buddhism and Jainism, exploring the nature of Brahman, Atman, and moksha.",
        "language": "Sanskrit",
        "file": "upanishads.json",
    },
]


def seed_book(db: Session, book: dict):
    existing = db.query(Scripture).filter_by(short_name=book["short_name"]).first()
    if existing:
        print(f"{book['name']} already seeded. Skipping.")
        return

    data_file = DATA_DIR / book["file"]
    if not data_file.exists():
        print(f"  WARNING: {book['file']} not found. Skipping {book['name']}.")
        return

    verses_data = json.loads(data_file.read_text())
    print(f"Seeding {book['name']} ({len(verses_data)} verses)...")

    scripture = Scripture(
        name=book["name"],
        short_name=book["short_name"],
        description=book["description"],
        language=book["language"],
    )
    db.add(scripture)
    db.flush()

    for i, v in enumerate(verses_data):
        verse = Verse(
            scripture_id=scripture.id,
            chapter=v.get("chapter", 1),
            verse_number=str(v.get("verse_number", i + 1)),
            sanskrit=v.get("sanskrit", "").strip(),
            transliteration=v.get("transliteration", "").strip(),
        )
        db.add(verse)
        db.flush()

        if v.get("translation"):
            db.add(VerseTranslation(
                verse_id=verse.id,
                language_code="en",
                author=v.get("author", "Traditional"),
                translation=v["translation"].strip(),
                meaning=v.get("meaning", ""),
            ))

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(verses_data)} inserted...")

    db.commit()
    print(f"  Done! {len(verses_data)} verses seeded for {book['name']}.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        for book in BOOKS:
            seed_book(db, book)
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
