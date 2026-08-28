"""NUVYRA health-information companion with optional AI generation."""
import os
import re
from typing import Tuple

import httpx

SYSTEM_DISCLAIMER = (
    "NUVYRA is a research platform. Its digital-biomarker features and stability index "
    "are experimental and are not clinically validated or a diagnosis."
)

EMERGENCY_PATTERNS = (
    r"can't breathe", r"cannot breathe", r"severe breathing", r"chest pain",
    r"unconscious", r"fainted", r"fainting", r"severe bleeding", r"stroke symptoms",
    r"suicid", r"overdose",
)
HEALTH_WORDS = (
    "health", "symptom", "disease", "illness", "condition", "medicine", "medication",
    "drug", "treatment", "therapy", "diagnos", "doctor", "hospital", "pain", "fever",
    "cough", "breath", "blood", "heart", "lung", "brain", "sleep", "stress", "anxiety",
    "nutrition", "vitamin", "test", "scan", "mri", "ct", "x-ray", "cbc", "hemoglobin",
    "diabetes", "cancer", "infection", "allergy", "asthma", "blood pressure", "cholesterol",
    "exercise", "hydration", "healthcare", "medical",
)


def _category(message: str) -> str:
    q = message.lower()
    if any(re.search(pattern, q) for pattern in EMERGENCY_PATTERNS):
        return "safety"
    if any(word in q for word in HEALTH_WORDS):
        return "health"
    if any(word in q for word in ("baseline", "trend", "biomarker", "voice", "facial", "blink", "gait", "movement", "nuvyra", "stability")):
        return "research"
    return "health"


def _fallback(message: str, language: str) -> Tuple[str, str]:
    q = message.lower()
    category = _category(message)
    if category == "safety":
        en = "If you are having a severe or rapidly worsening symptom, especially serious breathing difficulty, chest pain, loss of consciousness, or another emergency, seek urgent medical care now. NUVYRA cannot assess an emergency."
    elif "breathing" in q or "respiratory" in q:
        en = "Breathing-related measurements can describe breathing rate, timing, rhythm, and changes across a recording. NUVYRA treats these as research signals and can compare them with your own usable history. Activity, posture, talking, stress, illness, and recording quality can change these signals, so one result does not diagnose a condition."
    elif "blink" in q or "eye" in q:
        en = "Eye and blink measurements describe observable patterns such as blink frequency, timing, and eye opening. They can change with tiredness, attention, lighting, screen use, irritation, and camera quality. NUVYRA uses them as one research signal, not a diagnosis."
    elif "voice" in q or "speech" in q:
        en = "Voice and speech measurements can include speaking rate, pauses, pitch-related patterns, intensity, and changes in the recorded signal. They naturally vary with tiredness, stress, congestion, hydration, language, and microphone quality. NUVYRA looks for patterns over time rather than diagnosing from one recording."
    elif "gait" in q or "walking" in q or "movement" in q:
        en = "Movement and gait measurements describe observable features of movement, such as timing, speed-related patterns, or changes between steps when the recording supports them. They can be affected by footwear, surface, camera position, fatigue, and activity."
    elif "baseline" in q:
        en = "A personal baseline is a picture of your own usual pattern built from usable previous check-ins. Comparing you with yourself can be more useful than assuming one universal number is ideal for everyone."
    elif "diabetes" in q:
        en = "Diabetes is a group of conditions in which blood glucose is higher than the body can properly regulate. Different types have different causes and treatments. Diagnosis requires appropriate clinical assessment and testing; NUVYRA cannot diagnose diabetes."
    elif "blood pressure" in q:
        en = "Blood pressure is the force of blood pushing against artery walls. It changes during the day and can be affected by activity, stress, sleep, caffeine, medicines, and measurement technique. Repeated readings are best interpreted in context by a healthcare professional."
    elif "mri" in q:
        en = "MRI, or magnetic resonance imaging, uses a strong magnetic field and radio waves to create detailed images inside the body. Unlike an X-ray, it does not use ionizing radiation. Your healthcare team can explain why a particular MRI is recommended."
    else:
        en = "I can explain healthcare topics in simple language, including symptoms, conditions, medicines, tests, reports, prevention, lifestyle, and NUVYRA's voice, face, eye, movement, breathing, baseline, and trend measurements. I provide health information, not diagnosis or treatment decisions."
    if language == "hi":
        return "मैं स्वास्थ्य विषयों और NUVYRA के measurements को आसान भाषा में समझा सकता हूँ। " + en + " मैं diagnosis या treatment का निर्णय नहीं दे सकता।", category
    if language == "fr":
        return "Je peux expliquer les sujets de santé et les mesures de NUVYRA en termes simples. " + en + " Je ne peux pas poser de diagnostic ni décider d'un traitement.", category
    return en, category


def _model_answer(message: str, language: str) -> str | None:
    api_key = os.getenv("NUVYRA_DOCUMENT_AI_API_KEY", "").strip()
    base_url = os.getenv("NUVYRA_DOCUMENT_AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("NUVYRA_DOCUMENT_AI_MODEL", "gpt-4.1-mini").strip()
    if not api_key:
        return None
    language_name = {"en": "English", "hi": "Hindi", "fr": "French"}.get(language, "English")
    system = f"""You are NUVYRA Companion, a friendly health-information assistant. Answer the user's question directly in {language_name}, using simple language for someone with no medical background. You can explain general healthcare, symptoms, conditions, anatomy, medicines, tests, reports, prevention, lifestyle, and NUVYRA measurements. Do not diagnose, rule out, or confirm diseases. Do not prescribe, stop, or change medicines or doses. For severe or emergency symptoms, advise urgent professional care. For NUVYRA, explain voice/speech, facial dynamics, eyes/blinking, gait/movement, breathing, head movement, data quality, personal baseline, multimodal fusion, longitudinal trends, and AI analysis as experimental research signals, never as clinically validated diagnosis. If personal NUVYRA data is not supplied, never invent it. Be concise but useful."""
    payload = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": message}], "temperature": 0.2, "max_tokens": 700}
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            return content.strip() if isinstance(content, str) and content.strip() else None
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        return None


def answer(message: str, language: str = "en") -> tuple[str, str, str]:
    category = _category(message)
    text = _model_answer(message, language)
    if text is None:
        text, category = _fallback(message, language)
    return text, category, SYSTEM_DISCLAIMER
