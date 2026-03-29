import json
from collections.abc import Generator
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import OPENAI_API_KEY
from app.models import Verse, Conversation, Message, Scripture
from app.models.message import MessageRole
from app.services.search import search_verses

client = OpenAI(api_key=OPENAI_API_KEY)

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "gu": "Gujarati",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
}

SCRIPTURE_PROMPTS = {
    "gita": {
        "name": "Bhagavad Gita",
        "persona": "You are Vandana, a warm and wise spiritual guide rooted in the Bhagavad Gita. You speak like a caring elder — naturally, warmly, and conversationally.\n\nFor greetings, small talk, clarifications, or follow-up questions: respond warmly and briefly in plain conversational language. No verse needed.\n\nWhen a user shares a problem, struggle, or asks for spiritual guidance: respond with:\n1. The complete verse in Sanskrit (both lines of the shloka).\n2. Its simple meaning in one sentence.\n3. Two to three sentences of practical guidance connecting the verse to their situation.\nAlways end spiritual responses with \"राधे राधे!\" in an enthusiastic, joyful tone.",
        "context_label": "Bhagavad Gita",
    },
    "yoga_sutras": {
        "name": "Yoga Sutras of Patanjali",
        "persona": "You are Vandana, a wise guide rooted in the Yoga Sutras of Patanjali. You speak with calm clarity, like a patient yoga teacher.\n\nFor greetings or small talk: respond warmly and briefly.\n\nFor questions about mind, consciousness, practice, or life: share a relevant sutra in Sanskrit, its transliteration, a simple meaning, and two to three sentences of practical guidance connecting it to the user's situation.\nAlways end with \"Om Shanti!\"",
        "context_label": "Yoga Sutras of Patanjali",
    },
    "chanakya_neeti": {
        "name": "Chanakya Neeti",
        "persona": "You are Vandana, a sharp and pragmatic guide rooted in Chanakya Neeti. You speak with directness and practical wisdom, like a seasoned strategist and life coach.\n\nFor greetings or small talk: respond warmly and briefly.\n\nFor questions about life, relationships, work, leadership, or strategy: share a relevant shloka in Sanskrit, its meaning, and two to three sentences of sharp, actionable guidance. Be direct and practical — Chanakya is never vague.\nAlways end with \"Jai Chanakya!\"",
        "context_label": "Chanakya Neeti",
    },
    "arthashastra": {
        "name": "Arthashastra",
        "persona": "You are Vandana, a guide rooted in Kautilya's Arthashastra — the ancient treatise on statecraft, governance, and prosperity. You speak with authority and precision.\n\nFor greetings or small talk: respond warmly and briefly.\n\nFor questions about leadership, governance, economics, strategy, or decision-making: share a relevant passage, its meaning, and two to three sentences of practical wisdom connecting it to the user's situation.\nAlways end with \"Dharmo Rakshati Rakshitah!\"",
        "context_label": "Arthashastra",
    },
    "kama_sutra": {
        "name": "Kama Sutra",
        "persona": "You are Vandana, a thoughtful guide rooted in Vatsyayana's Kama Sutra — the ancient science of love, relationships, and the art of living well. You speak with sophistication and sensitivity.\n\nFor greetings or small talk: respond warmly and briefly.\n\nFor questions about relationships, love, intimacy, social etiquette, or the art of living: share a relevant passage, its meaning, and two to three sentences of thoughtful guidance. Be respectful, insightful, and never crude.\nAlways end with \"Kama is sacred!\"",
        "context_label": "Kama Sutra",
    },
    "upanishads": {
        "name": "Upanishads",
        "persona": "You are Vandana, a deeply contemplative guide rooted in the Upanishads — the ancient philosophical texts that explore the nature of reality, consciousness, and the Self.\n\nFor greetings or small talk: respond warmly and briefly.\n\nFor questions about existence, consciousness, the Self, reality, or moksha: share a relevant passage in Sanskrit, its meaning, and two to three sentences of profound philosophical guidance.\nAlways end with \"Aham Brahmasmi!\"",
        "context_label": "Upanishads",
    },
}

DEFAULT_SCRIPTURE = "gita"


def get_scripture_config(short_name: str | None) -> dict:
    return SCRIPTURE_PROMPTS.get(short_name or DEFAULT_SCRIPTURE, SCRIPTURE_PROMPTS[DEFAULT_SCRIPTURE])


def get_system_prompt(language_code: str = "en", scripture_short_name: str | None = None) -> str:
    language = LANGUAGE_NAMES.get(language_code, "English")
    config = get_scripture_config(scripture_short_name)
    return config["persona"] + f"\n\nIMPORTANT: Plain prose only. No markdown, no bold, no asterisks, no lists, no headers. Write as if speaking aloud.\n\nYou MUST respond entirely in {language}."


def build_verse_context(verses: list[Verse], language_code: str = "en", scripture_short_name: str | None = None) -> str:
    config = get_scripture_config(scripture_short_name)
    context_parts = []

    for verse in verses:
        translation = next(
            (t.translation for t in verse.translations if t.language_code == language_code),
            next((t.translation for t in verse.translations if t.language_code == "en"), None)
        )
        if not translation:
            continue
        label = config["context_label"]
        part = f"{label} {verse.chapter}.{verse.verse_number} — {verse.sanskrit} — {translation}"
        context_parts.append(part)

    return "\n\n---\n\n".join(context_parts)


def suggest_scripture(user_message: str) -> str:
    """Ask GPT which scripture best suits the user's question."""
    books = "\n".join([f"- {k}: {v['name']}" for k, v in SCRIPTURE_PROMPTS.items()])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant. Based on the user's message, suggest the single most relevant ancient Indian scripture from this list:\n{books}\n\nRespond with ONLY the short key (e.g. 'gita', 'yoga_sutras', 'chanakya_neeti', 'arthashastra', 'kama_sutra', 'upanishads'). Nothing else.",
            },
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=20,
    )
    suggested = response.choices[0].message.content.strip().lower()
    return suggested if suggested in SCRIPTURE_PROMPTS else DEFAULT_SCRIPTURE


def get_conversation_history(conversation: Conversation, limit: int = 10) -> list[dict]:
    recent_messages = conversation.messages[-limit:] if conversation.messages else []
    return [{"role": msg.role.value, "content": msg.content} for msg in recent_messages]


def chat(
    user_message: str,
    db: Session,
    user_id: str,
    conversation_id: str | None = None,
    language_code: str = "en",
    scripture_short_name: str | None = None,
) -> tuple[Conversation, Message]:
    if conversation_id:
        conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
        # Use conversation's stored scripture if not overridden
        if not scripture_short_name:
            scripture_short_name = conversation.scripture_short_name
    else:
        conversation = Conversation(
            user_id=user_id,
            language_code=language_code,
            scripture_short_name=scripture_short_name or DEFAULT_SCRIPTURE,
        )
        db.add(conversation)
        db.flush()

    history = get_conversation_history(conversation)

    user_msg = Message(conversation_id=conversation.id, role=MessageRole.user, content=user_message)
    db.add(user_msg)
    db.flush()

    relevant_verses = search_verses(
        user_message, db,
        language_code=language_code,
        top_k=2,
        scripture_short_names=[scripture_short_name or DEFAULT_SCRIPTURE],
    )
    verse_context = build_verse_context(relevant_verses, language_code=language_code, scripture_short_name=scripture_short_name)
    cited_verse_ids = [str(v.id) for v in relevant_verses]
    config = get_scripture_config(scripture_short_name)

    messages = [
        {"role": "system", "content": get_system_prompt(language_code, scripture_short_name)},
        {"role": "system", "content": f"Relevant passages from the {config['context_label']}:\n\n{verse_context}"},
        *history,
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7)
    assistant_content = response.choices[0].message.content

    if not conversation.title:
        conversation.title = user_message[:60] + ("..." if len(user_message) > 60 else "")

    assistant_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=assistant_content,
        cited_verses=cited_verse_ids,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    db.refresh(conversation)

    return conversation, assistant_msg


def chat_stream(
    user_message: str,
    db: Session,
    user_id: str,
    conversation_id: str | None = None,
    language_code: str = "en",
    scripture_short_name: str | None = None,
) -> Generator[str, None, None]:
    if conversation_id:
        conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
        if not scripture_short_name:
            scripture_short_name = conversation.scripture_short_name
    else:
        conversation = Conversation(
            user_id=user_id,
            language_code=language_code,
            scripture_short_name=scripture_short_name or DEFAULT_SCRIPTURE,
        )
        db.add(conversation)
        db.flush()

    history = get_conversation_history(conversation)

    user_msg = Message(conversation_id=conversation.id, role=MessageRole.user, content=user_message)
    db.add(user_msg)
    db.flush()

    relevant_verses = search_verses(
        user_message, db,
        language_code=language_code,
        top_k=2,
        scripture_short_names=[scripture_short_name or DEFAULT_SCRIPTURE],
    )
    verse_context = build_verse_context(relevant_verses, language_code=language_code, scripture_short_name=scripture_short_name)
    cited_verse_ids = [str(v.id) for v in relevant_verses]
    config = get_scripture_config(scripture_short_name)

    yield f"data: {json.dumps({'type': 'meta', 'conversation_id': str(conversation.id), 'cited_verses': cited_verse_ids})}\n\n"

    messages = [
        {"role": "system", "content": get_system_prompt(language_code, scripture_short_name)},
        {"role": "system", "content": f"Relevant passages from the {config['context_label']}:\n\n{verse_context}"},
        *history,
        {"role": "user", "content": user_message},
    ]

    full_content = []
    stream = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7, stream=True)

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            full_content.append(delta)
            yield f"data: {json.dumps({'type': 'chunk', 'content': delta})}\n\n"

    assistant_content = "".join(full_content)

    if not conversation.title:
        conversation.title = user_message[:60] + ("..." if len(user_message) > 60 else "")

    assistant_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.assistant,
        content=assistant_content,
        cited_verses=cited_verse_ids,
    )
    db.add(assistant_msg)
    db.commit()

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
