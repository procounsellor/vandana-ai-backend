import json
from collections.abc import Generator
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import OPENAI_API_KEY
from app.models import Verse, Conversation, Message
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

BASE_SYSTEM_PROMPT = """You are Vandana, a spiritual guide rooted in the Bhagavad Gita.

When a user shares a problem, respond in this exact structure — keep it short and spoken naturally:

1. The complete verse in Sanskrit (include both lines of the shloka).
2. Its simple meaning in one sentence.
3. Two to three sentences of practical guidance connecting the verse to their situation.

Do not greet, do not repeat the user's question, do not give lengthy explanations. Get straight to the verse and its wisdom. Always end your response with "राधे राधे!" in an enthusiastic, joyful tone.

IMPORTANT: Plain prose only. No markdown, no bold, no asterisks, no lists, no headers. Write as if speaking aloud.

You MUST respond entirely in {language}. Do not use any other language for the explanation or guidance."""


def get_system_prompt(language_code: str = "en") -> str:
    language = LANGUAGE_NAMES.get(language_code, "English")
    return BASE_SYSTEM_PROMPT.format(language=language)


def build_verse_context(verses: list[Verse], language_code: str = "en") -> str:
    """Format retrieved verses into a context block for the LLM."""
    context_parts = []

    for verse in verses:
        translation = next(
            (t.translation for t in verse.translations
             if t.language_code == language_code and t.author == "Swami Sivananda"),
            next((t.translation for t in verse.translations if t.language_code == "en"), None)
        )

        if not translation:
            continue

        part = (
            f"Bhagavad Gita Chapter {verse.chapter}, Verse {verse.verse_number}\n"
            f"Sanskrit: {verse.sanskrit}\n"
            f"Transliteration: {verse.transliteration}\n"
            f"Translation: {translation}"
        )
        context_parts.append(part)

    return "\n\n---\n\n".join(context_parts)


def get_conversation_history(conversation: Conversation, limit: int = 10) -> list[dict]:
    """Get recent messages formatted for the OpenAI API."""
    recent_messages = conversation.messages[-limit:] if conversation.messages else []
    return [
        {"role": msg.role.value, "content": msg.content}
        for msg in recent_messages
    ]


def chat(
    user_message: str,
    db: Session,
    user_id: str,
    conversation_id: str | None = None,
    language_code: str = "en",
) -> tuple[Conversation, Message]:
    """
    Main chat function:
    1. Get or create conversation
    2. Search for relevant verses
    3. Call GPT with context
    4. Save and return messages
    """

    # Get or create conversation
    if conversation_id:
        conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
    else:
        conversation = Conversation(user_id=user_id, language_code=language_code)
        db.add(conversation)
        db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=user_message,
    )
    db.add(user_msg)
    db.flush()

    # Search for relevant verses
    relevant_verses = search_verses(user_message, db, language_code=language_code, top_k=3)
    verse_context = build_verse_context(relevant_verses, language_code=language_code)
    cited_verse_ids = [str(v.id) for v in relevant_verses]

    # Build messages for OpenAI
    history = get_conversation_history(conversation)
    messages = [
        {"role": "system", "content": get_system_prompt(language_code)},
        {
            "role": "system",
            "content": f"Relevant verses from the Bhagavad Gita:\n\n{verse_context}"
        },
        *history,
        {"role": "user", "content": user_message},
    ]

    # Call GPT
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    assistant_content = response.choices[0].message.content

    # Auto-generate conversation title from first message
    if not conversation.title:
        conversation.title = user_message[:60] + ("..." if len(user_message) > 60 else "")

    # Save assistant message
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
) -> Generator[str, None, None]:
    """
    Streaming version of chat. Yields SSE-formatted chunks as GPT generates them.
    Saves the full response to DB once streaming is complete.
    """

    # Get or create conversation
    if conversation_id:
        conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
        if not conversation:
            raise ValueError("Conversation not found")
    else:
        conversation = Conversation(user_id=user_id, language_code=language_code)
        db.add(conversation)
        db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.user,
        content=user_message,
    )
    db.add(user_msg)
    db.flush()

    # Search for relevant verses
    relevant_verses = search_verses(user_message, db, language_code=language_code, top_k=3)
    verse_context = build_verse_context(relevant_verses, language_code=language_code)
    cited_verse_ids = [str(v.id) for v in relevant_verses]

    # Send conversation_id first so client knows which conversation this belongs to
    yield f"data: {json.dumps({'type': 'meta', 'conversation_id': str(conversation.id), 'cited_verses': cited_verse_ids})}\n\n"

    # Build messages for OpenAI
    history = get_conversation_history(conversation)
    messages = [
        {"role": "system", "content": get_system_prompt(language_code)},
        {"role": "system", "content": f"Relevant verses from the Bhagavad Gita:\n\n{verse_context}"},
        *history,
        {"role": "user", "content": user_message},
    ]

    # Stream GPT response
    full_content = []
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            full_content.append(delta)
            yield f"data: {json.dumps({'type': 'chunk', 'content': delta})}\n\n"

    # Save full assistant message to DB
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
