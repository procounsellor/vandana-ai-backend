import base64
import requests
from app.config import SIMLI_API_KEY, SIMLI_FACE_ID

SIMLI_STATIC_URL = "https://api.simli.ai/static/audio"


def generate_avatar_video(audio_bytes: bytes) -> dict:
    """
    Generate a lip-synced avatar video from WAV audio bytes using Simli.
    Audio must be 16kHz mono WAV (matches Sarvam TTS output).
    Returns dict with hls_url and mp4_url.
    """
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    response = requests.post(
        SIMLI_STATIC_URL,
        headers={
            "x-simli-api-key": SIMLI_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "faceId": SIMLI_FACE_ID,
            "audioBase64": audio_base64,
            "audioFormat": "wav",
            "audioSampleRate": 16000,
            "audioChannelCount": 1,
            "videoStartingFrame": 0,
        },
        timeout=60,
    )
    if not response.ok:
        print(f"Simli error {response.status_code}: {response.text}")
        response.raise_for_status()
    result = response.json()
    print(f"Simli response: {result}")
    return result
