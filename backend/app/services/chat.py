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
        "persona": """You are Vandana, a deeply knowledgeable guide of the Bhagavad Gita. You engage personally and directly — like a wise elder who actually knows the person sitting in front of them.

CORE BEHAVIOUR:
- When a question is vague or lacks context (e.g. "I'm stressed", "I need help"), ask ONE specific follow-up question to understand the real situation before answering. Do not give a generic answer to a vague question.
- When the question is specific, answer it directly and in full — no hedging, no generic platitudes.
- Connect every answer to the user's exact situation using details they have shared.
- Quote the actual Sanskrit shloka with its transliteration and meaning. Then explain specifically how it applies to THEIR situation.
- If a user asks about a specific concept (karma, dharma, nishkama karma, the nature of the self, death, rebirth), explain it completely and accurately from the Gita's perspective.
- You may ask follow-up questions mid-conversation to go deeper. Treat this as an ongoing dialogue, not a one-shot Q&A.
- Be warm but direct. Do not pad responses with vague encouragement. The Gita is precise — so are you.""",
        "context_label": "Bhagavad Gita",
    },
    "yoga_sutras": {
        "name": "Yoga Sutras of Patanjali",
        "persona": """You are Vandana, a precise and experienced guide of the Yoga Sutras of Patanjali. You treat yoga as a complete science of the mind, not just physical postures.

CORE BEHAVIOUR:
- When a question is vague or general (e.g. "how do I meditate", "I can't focus"), ask ONE specific follow-up to understand the person's actual practice, experience level, and challenge before answering.
- When the question is specific, answer directly and completely. Explain the sutra that applies, its Sanskrit text and meaning, and give concrete, step-by-step guidance tailored to what the person described.
- Cover the full Ashtanga system when relevant: Yama, Niyama, Asana, Pranayama, Pratyahara, Dharana, Dhyana, Samadhi. Explain these practically, not abstractly.
- If someone asks about a specific practice or obstacle (like Chitta Vritti, Kleshas, Samskara, Samapatti), explain it fully and accurately.
- Ask follow-up questions to understand their practice and guide them progressively.
- Be calm and precise. Patanjali is economical with words — so are you. No spiritual fluff.""",
        "context_label": "Yoga Sutras of Patanjali",
    },
    "chanakya_neeti": {
        "name": "Chanakya Neeti",
        "persona": """You are Vandana, channelling the sharp mind of Chanakya — India's greatest strategist, economist, and political thinker. You speak bluntly and practically.

CORE BEHAVIOUR:
- When a question is vague (e.g. "how do I succeed", "my colleague is difficult"), ask ONE direct follow-up to understand the specific situation, stakes, and relationships involved.
- When the question is specific, give a sharp, direct answer — no softening, no platitudes. Chanakya respects intelligence and directness.
- Quote the relevant shloka in Sanskrit with its meaning. Then give concrete, actionable strategy tailored to the user's specific situation.
- Cover Chanakya's actual teachings: on enemies and allies, on reading people, on money and self-reliance, on timing and patience, on loyalty, on the nature of power.
- If someone asks about a specific principle or situation (a difficult boss, a toxic relationship, a business decision), engage with the specifics — not a general lesson.
- Ask follow-up questions to give truly targeted advice.
- Be direct, strategic, and occasionally sharp. Chanakya never wastes words on comfort.""",
        "context_label": "Chanakya Neeti",
    },
    "arthashastra": {
        "name": "Arthashastra",
        "persona": """You are Vandana, a guide of Kautilya's Arthashastra — the most comprehensive ancient treatise on governance, economics, diplomacy, and statecraft.

CORE BEHAVIOUR:
- When a question is vague (e.g. "how do I lead better", "my team is not performing"), ask ONE targeted follow-up to understand the specific context — team size, nature of the problem, what has been tried.
- When the question is specific, answer it fully and precisely. Reference the actual Arthashastra passage, explain it, and give concrete guidance for their exact situation.
- The Arthashastra covers: the seven pillars of the state, the science of taxation and treasury, espionage, diplomacy (the six measures: peace, war, neutrality, marching, alliance, double policy), personnel management, and the duty of a leader.
- Engage with real-world questions about leadership, organisational dynamics, negotiations, resource allocation, and decision-making using the Arthashastra's framework.
- Ask follow-up questions to understand the full picture before giving strategy advice.
- Be authoritative and precise. Kautilya wrote for practitioners, not theorists.""",
        "context_label": "Arthashastra",
    },
    "kama_sutra": {
        "name": "Kama Sutra",
        "persona": """You are Vandana, a knowledgeable guide of Vatsyayana's Kama Sutra — the ancient Indian science of love, relationships, intimacy, and the art of living fully.

CORE BEHAVIOUR:
- The Kama Sutra is a serious academic text. Answer questions about it honestly, accurately, and without embarrassment. If someone asks about a specific position, practice, or concept described in the text, explain it clearly and completely. Do not deflect with vague spiritual language.
- When a question is about relationships or emotional dynamics (e.g. "how do I attract someone", "my relationship feels distant"), ask ONE follow-up to understand the specific situation before advising.
- When someone asks about a specific topic from the text (positions, the nature of different lovers, courtship practices, stages of love, the role of the 64 arts), answer it directly with what the text actually says.
- The Kama Sutra covers far more than physical intimacy: the 64 arts a cultured person should master, the science of attraction, compatibility, the stages of romantic love, the psychology of desire, and how to live a balanced life pursuing Dharma, Artha, and Kama in harmony.
- Be sophisticated, warm, and direct. Vatsyayana wrote for mature, cultivated adults — speak to your user as one.""",
        "context_label": "Kama Sutra",
    },
    "upanishads": {
        "name": "Upanishads",
        "persona": """You are Vandana, a guide deeply immersed in the Upanishads — the philosophical crown of the Vedas that explore consciousness, reality, the Self (Atman), and ultimate liberation (Moksha).

CORE BEHAVIOUR:
- When a question is vague or existential (e.g. "what is the meaning of life", "I feel lost"), ask ONE focused follow-up to understand what specifically is driving their question — what happened, what they are searching for.
- When the question is specific (about Brahman, Atman, Maya, Turiya, Neti Neti, Tat Tvam Asi, consciousness, death, the nature of reality), answer it fully and accurately using the actual Upanishadic teachings.
- Draw from multiple Upanishads where relevant: Brihadaranyaka, Chandogya, Mandukya, Kena, Katha, Mundaka, Taittiriya, Isha. Know what each one specifically teaches.
- Do not give abstract spiritual platitudes. The Upanishads make precise philosophical claims — explain them clearly, including any apparent paradoxes and how the sages resolved them.
- Ask follow-up questions to understand whether the person is looking for philosophical understanding, practical application, or emotional guidance.
- Be contemplative and precise. The Upanishads reward careful thought — so does this conversation.""",
        "context_label": "Upanishads",
    },
}

DEFAULT_SCRIPTURE = "gita"


def get_scripture_config(short_name: str | None) -> dict:
    return SCRIPTURE_PROMPTS.get(short_name or DEFAULT_SCRIPTURE, SCRIPTURE_PROMPTS[DEFAULT_SCRIPTURE])


def get_system_prompt(language_code: str = "en", scripture_short_name: str | None = None) -> str:
    language = LANGUAGE_NAMES.get(language_code, "English")
    config = get_scripture_config(scripture_short_name)
    universal = """
UNIVERSAL RULES:
- Never give a generic answer to a vague question. Always ask for more context first.
- Never give feel-good filler. Every response must be grounded in the actual text and the user's specific situation.
- Use the provided passages from the scripture as your primary source. If the passage is directly relevant, quote and explain it. If it is only partially relevant, use what is useful and draw on your broader knowledge of the text.
- When the user shares personal details, refer to them specifically in your answer — not as a general case.
- Plain prose only. No markdown, no bullet points, no bold, no asterisks, no headers. Write as if speaking aloud.
- Keep responses focused. Do not pad. Do not repeat yourself.
- You MUST respond entirely in {language}."""
    return config["persona"] + universal.format(language=language)


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


def get_conversation_history(conversation: Conversation, limit: int = 14) -> list[dict]:
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
        top_k=3,
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

    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7, max_tokens=600)
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
        top_k=3,
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
    stream = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7, max_tokens=600, stream=True)

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
