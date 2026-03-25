import base64
import io
import re
import wave
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections.abc import Generator
from pedalboard import Pedalboard, Reverb, Delay, HighShelfFilter
from app.config import SARVAM_API_KEY

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"

# Language code mapping from our app's language_code to Sarvam's format
LANGUAGE_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "te": "te-IN",
    "ta": "ta-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "gu": "gu-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "pa": "pa-IN",
}

TTS_MODEL = "bulbul:v2"

TTS_SPEAKERS = {
    "en": "abhilash",
    "hi": "abhilash",
    "te": "abhilash",
    "ta": "abhilash",
    "kn": "abhilash",
    "ml": "abhilash",
    "gu": "abhilash",
    "mr": "abhilash",
    "bn": "abhilash",
    "pa": "abhilash",
}


CHUNK_MAX_BYTES = 400  # UTF-8 bytes — Devanagari is 3 bytes/char, so 400 bytes ≈ 130 Hindi chars (~1 sentence)


def _clean_for_tts(text: str) -> str:
    """Strip markdown formatting so TTS reads cleanly."""
    # Remove markdown headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Strip bold/italic asterisks and underscores
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"_+", "", text)
    # Remove numbered list prefixes
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # Remove bullet points
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
    # Remove backticks
    text = re.sub(r"`+", "", text)
    # Replace dandas with period+space so each line becomes its own sentence boundary
    text = text.replace('॥', '. ')
    text = text.replace('।', '. ')
    # Collapse newlines to spaces
    text = re.sub(r"\n+", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _split_text(text: str, max_bytes: int = CHUNK_MAX_BYTES) -> list[str]:
    """Split text into chunks measured by UTF-8 bytes (handles multi-byte scripts like Devanagari)."""
    text = text.strip()
    if len(text.encode("utf-8")) <= max_bytes:
        return [text]

    chunks = []
    while len(text.encode("utf-8")) > max_bytes:
        # Binary search: find max character count whose UTF-8 encoding fits in max_bytes
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if len(text[:mid].encode("utf-8")) <= max_bytes:
                lo = mid
            else:
                hi = mid - 1
        limit = lo

        # Split at sentence boundary (dandas already replaced with . and , by clean step)
        split_at = -1
        for punct in [". ", "! ", "? "]:
            pos = text.rfind(punct, 0, limit)
            if pos > split_at:
                split_at = pos + len(punct)

        if split_at <= 0:
            split_at = text.rfind(" ", 0, limit)
        if split_at <= 0:
            split_at = limit

        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()

    if text:
        chunks.append(text)

    return chunks


def _is_shloka(text: str) -> bool:
    """Pure Devanagari with no ASCII letters → likely a Sanskrit shloka line."""
    return not bool(re.search(r'[a-zA-Z]', text)) and bool(re.search(r'[\u0900-\u097F]', text))


def apply_temple_effects(wav_bytes: bytes) -> bytes:
    """Apply reverb, echo, EQ, and gentle slowdown to give a temple/godly feel."""
    # Read WAV
    with wave.open(io.BytesIO(wav_bytes)) as wf:
        sr = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    # Convert int16 → float32 [-1, 1]
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

    # Effects chain — new instance per call (Reverb/Delay are stateful)
    board = Pedalboard([
        HighShelfFilter(cutoff_frequency_hz=6000, gain_db=-2),   # gentle high trim
        Reverb(room_size=0.45, damping=0.55, wet_level=0.25, dry_level=0.75),  # temple space
        Delay(delay_seconds=0.08, feedback=0.15, mix=0.08),      # subtle echo
    ])
    processed = board(audio, sr)
    processed = np.clip(processed, -1.0, 1.0)
    audio_int16 = (processed * 32767).astype(np.int16)

    # Very gentle slowdown (0.97x) — just a touch slower, minimal pitch shift
    out_sr = int(sr * 0.97)
    out = io.BytesIO()
    with wave.open(out, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(out_sr)
        wf.writeframes(audio_int16.tobytes())
    return out.getvalue()


def _tts_chunk(text: str, sarvam_lang: str, speaker: str) -> bytes:
    """Call Sarvam TTS for a single chunk and return processed WAV bytes."""
    if not text.strip():
        return b''
    pace = 0.75 if _is_shloka(text) else 0.9
    response = requests.post(
        SARVAM_TTS_URL,
        headers={"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "target_language_code": sarvam_lang,
            "model": TTS_MODEL,
            "speaker": speaker,
            "pace": pace,
            "speech_sample_rate": 16000,
            "output_audio_codec": "wav",
        },
        timeout=30,
    )
    if not response.ok:
        print(f"Sarvam TTS error {response.status_code}: {response.text}")
        response.raise_for_status()
    raw_wav = base64.b64decode(response.json()["audios"][0])
    return apply_temple_effects(raw_wav)


def text_to_speech_stream(text: str, language_code: str = "en") -> Generator[bytes, None, None]:
    """
    Convert text to speech, yielding each WAV chunk as soon as it is ready (in order).
    All Sarvam calls run in parallel; chunks are yielded in original text order.
    """
    sarvam_lang = LANGUAGE_MAP.get(language_code, "en-IN")
    speaker = TTS_SPEAKERS.get(language_code, "anushka")
    text = _clean_for_tts(text)
    chunks = _split_text(text)

    print(f"TTS: {len(chunks)} chunks, bytes={[len(c.encode('utf-8')) for c in chunks]}")
    for i, c in enumerate(chunks):
        print(f"  Chunk {i+1}: {c[:80]}...")

    if not chunks:
        return

    pending: dict[int, bytes] = {}
    next_idx = 0

    with ThreadPoolExecutor(max_workers=min(len(chunks), 6)) as executor:
        future_to_idx = {executor.submit(_tts_chunk, chunk, sarvam_lang, speaker): i
                         for i, chunk in enumerate(chunks)}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            wav = future.result()
            if wav:
                pending[idx] = wav
                print(f"  Chunk {idx+1} ready, {len(wav)} bytes")
            # Yield consecutive ready chunks in order
            while next_idx in pending:
                yield pending.pop(next_idx)
                next_idx += 1

    # Yield any remaining (shouldn't happen, but safety)
    while next_idx in pending:
        yield pending.pop(next_idx)
        next_idx += 1


def text_to_speech(text: str, language_code: str = "en") -> list[bytes]:
    """Convenience wrapper — collects all streamed chunks into a list."""
    return list(text_to_speech_stream(text, language_code))


_MIME_MAP = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "webm": "audio/webm",
    "ogg": "audio/ogg",
    "m4a": "audio/mp4",
    "flac": "audio/flac",
}


def speech_to_text(audio_bytes: bytes, filename: str = "audio.webm", language_code: str = "en") -> str:
    """
    Convert speech to text using Sarvam AI.
    Sends audio directly without conversion — Sarvam accepts WebM/WAV/MP3/OGG natively.
    Returns the transcript string.
    """
    sarvam_lang = LANGUAGE_MAP.get(language_code, "en-IN")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    mime = _MIME_MAP.get(ext, "audio/webm")

    response = requests.post(
        SARVAM_STT_URL,
        headers={"api-subscription-key": SARVAM_API_KEY},
        files={"file": (filename, audio_bytes, mime)},
        data={
            "model": "saarika:v2.5",
            "language_code": sarvam_lang,
        },
        timeout=30,
    )
    if not response.ok:
        print(f"Sarvam STT error {response.status_code}: {response.text}")
        raise ValueError(f"Sarvam STT error {response.status_code}: {response.text}")
    return response.json().get("transcript", "")
