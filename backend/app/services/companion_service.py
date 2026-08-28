"""NUVYRA health-information companion with broad healthcare coverage."""
from __future__ import annotations

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
    r"suicid", r"overdose", r"seizure", r"difficulty breathing",
)

# Broad routing vocabulary. The companion still uses an LLM when configured;
# these rules make the offline fallback useful rather than returning one generic answer.
HEALTH_WORDS = (
    "health", "symptom", "disease", "illness", "condition", "medicine", "medication",
    "drug", "treatment", "therapy", "diagnos", "doctor", "hospital", "pain", "fever",
    "cough", "breath", "blood", "heart", "lung", "brain", "sleep", "stress", "anxiety",
    "nutrition", "vitamin", "test", "scan", "mri", "ct", "x-ray", "cbc", "hemoglobin",
    "diabetes", "cancer", "infection", "allergy", "asthma", "blood pressure", "cholesterol",
    "exercise", "hydration", "healthcare", "medical", "pregnan", "period", "headache",
    "nausea", "vomit", "diarrhea", "constipation", "rash", "weight", "kidney", "liver",
    "thyroid", "hormone", "vaccine", "immun", "antibiotic", "dosage", "side effect",
    "mental health", "depression", "panic", "dermat", "arthritis", "migraine", "stroke",
    "heart attack", "oxygen", "temperature", "pulse", "ecg", "eeg", "ultrasound", "biopsy",
)


def _category(message: str) -> str:
    q = message.lower()
    if any(re.search(pattern, q) for pattern in EMERGENCY_PATTERNS):
        return "safety"
    if any(word in q for word in HEALTH_WORDS):
        return "health"
    if any(word in q for word in (
        "baseline", "trend", "biomarker", "voice", "speech", "facial", "blink", "eye",
        "gait", "walking", "movement", "breathing", "head movement", "nuvyra", "stability",
    )):
        return "research"
    return "health"


def _fallback(message: str, language: str) -> Tuple[str, str]:
    q = message.lower().strip()
    category = _category(message)

    if category == "safety":
        en = (
            "If you are having a severe or rapidly worsening symptom, especially serious breathing "
            "difficulty, chest pain, loss of consciousness, severe bleeding, or another emergency, "
            "seek urgent medical care now. NUVYRA cannot assess an emergency."
        )
    elif any(k in q for k in ("breathing", "respiratory", "respiration")):
        en = (
            "Breathing-related measurements can describe breathing rate, timing, rhythm and how those "
            "patterns change during a recording. In NUVYRA they are research signals that can be compared "
            "with your own usable history. Activity, posture, talking, stress, illness and recording quality "
            "can affect them, so a single result cannot diagnose a condition."
        )
    elif any(k in q for k in ("blink", "blinking", "eye opening", "eye movement", "eyes")):
        en = (
            "Eye and blink measurements describe observable patterns such as blink frequency, timing and "
            "eye opening. They can change with tiredness, attention, lighting, screen use, irritation and "
            "camera quality. NUVYRA treats them as one research signal rather than a diagnosis."
        )
    elif any(k in q for k in ("voice", "speech", "speaking", "talking")):
        en = (
            "Voice and speech measurements can include speaking rate, pauses, pitch-related patterns, "
            "intensity and other properties of the recorded signal. They naturally vary with tiredness, "
            "stress, congestion, hydration, language and microphone quality. NUVYRA looks for changes over "
            "time rather than diagnosing from one recording."
        )
    elif any(k in q for k in ("gait", "walking", "walk", "movement")):
        en = (
            "Movement and gait measurements describe observable features such as timing, speed-related "
            "patterns, variability and symmetry when the recording supports them. They can be affected by "
            "surface, footwear, camera position, fatigue and activity. NUVYRA uses these as research signals."
        )
    elif any(k in q for k in ("head movement", "head motion")):
        en = (
            "Head-movement measurements describe how the head moves during a recording, including overall "
            "motion and changes in motion. Camera position and natural movement can affect the result. "
            "NUVYRA uses it as one research signal and does not use it to diagnose illness."
        )
    elif "baseline" in q:
        en = (
            "Your personal baseline is a picture of your own usual pattern built from usable previous "
            "check-ins. NUVYRA compares a new session with your history instead of assuming one universal "
            "number is ideal for everyone. The baseline becomes more useful as more good-quality observations accumulate."
        )
    elif any(k in q for k in ("biomarker", "digital biomarker")):
        en = (
            "A digital biomarker is a measurable signal collected from a digital device or software that may "
            "describe something about a person's behavior or physiology. NUVYRA studies several signals together, "
            "but its digital biomarkers are experimental and are not clinical diagnoses."
        )
    elif any(k in q for k in ("multimodal", "fusion", "multiple signals")):
        en = (
            "Multimodal analysis means looking at several kinds of signals together instead of relying on one "
            "measurement. NUVYRA can combine available voice, face, eye, movement, breathing, head-movement and "
            "self-reported signals. Missing or poor-quality signals are excluded rather than automatically treated as normal."
        )
    elif "diabetes" in q:
        en = (
            "Diabetes is a group of conditions in which blood glucose stays higher than the body can regulate properly. "
            "Different types have different causes. Diagnosis requires appropriate clinical assessment and testing; "
            "NUVYRA cannot diagnose diabetes."
        )
    elif "blood pressure" in q or "hypertension" in q:
        en = (
            "Blood pressure is the force of blood pushing against artery walls. It changes during the day and can be "
            "affected by activity, stress, sleep, caffeine, medicines and measurement technique. Repeated readings are "
            "usually more informative than one reading and should be interpreted in context by a healthcare professional."
        )
    elif "mri" in q:
        en = (
            "MRI, or magnetic resonance imaging, uses a strong magnetic field and radio waves to create detailed images "
            "inside the body. It does not use ionizing X-ray radiation. Whether an MRI is appropriate depends on the "
            "clinical question and your healthcare team's assessment."
        )
    elif any(k in q for k in ("cbc", "complete blood count")):
        en = (
            "A CBC, or complete blood count, measures several types of cells and related values in your blood, including "
            "red blood cells, white blood cells and platelets. Results can have many possible explanations, so individual "
            "values should be interpreted together with the reference range and clinical context."
        )
    elif "hemoglobin" in q:
        en = (
            "Hemoglobin is a protein in red blood cells that carries oxygen. A hemoglobin result can be influenced by "
            "many factors, and the meaning of a result depends on the laboratory reference range and the person's overall context."
        )
    elif any(k in q for k in ("heart rate", "pulse rate", "pulse")):
        en = (
            "Heart rate is the number of heartbeats per minute. It naturally changes with activity, fitness, emotions, "
            "temperature, sleep, medicines and illness. A single value is not enough to diagnose a heart problem."
        )
    elif any(k in q for k in ("fever", "temperature")):
        en = (
            "A fever means body temperature is elevated, often because the immune system is responding to an infection, "
            "although there are other possible causes. The importance of a temperature depends on the actual reading, age, "
            "symptoms and context."
        )
    elif any(k in q for k in ("anxiety", "panic attack", "panic")):
        en = (
            "Anxiety can involve worry, tension and physical sensations such as a faster heartbeat or changes in breathing. "
            "These experiences can have many causes. If anxiety is persistent, severe, or interfering with everyday life, "
            "talking with a healthcare or mental-health professional can help."
        )
    elif any(k in q for k in ("sleep", "insomnia")):
        en = (
            "Sleep supports memory, mood, attention and physical recovery. Sleep needs vary by age and person. Difficulty "
            "sleeping can have many causes, including schedule changes, stress, illness, medicines and environment. Persistent "
            "sleep problems are worth discussing with a healthcare professional."
        )
    elif any(k in q for k in ("medicine", "medication", "drug", "tablet", "pill", "side effect")):
        en = (
            "Medicines can have intended effects as well as side effects and interactions. The right medicine and dose depend "
            "on the person and the condition. I can explain general information about a medicine, but I should not tell you "
            "to start, stop or change a prescribed medicine without guidance from a qualified healthcare professional."
        )
    elif any(k in q for k in ("what is", "meaning of", "explain", "define", "why")):
        en = (
            "I can explain healthcare concepts in simple, everyday language. The meaning of a health finding usually depends "
            "on the person's symptoms, history, measurements and the relevant reference ranges. If you share the specific "
            "health term or question, I can explain what it generally means and what factors can affect it."
        )
    else:
        en = (
            "I can help explain healthcare topics in simple language, including symptoms, conditions, medicines, tests, "
            "reports, prevention, lifestyle and NUVYRA's voice, face, eye, movement, breathing, baseline and trend measurements. "
            "I provide health information, not diagnosis or treatment decisions."
        )

    if language == "hi":
        # Keep the substantive fallback useful even without an external model.
        return "मैं स्वास्थ्य विषयों को आसान भाषा में समझाने में मदद कर सकता हूँ।\n\n" + en + "\n\nमैं diagnosis नहीं करता और prescribed treatment या medicine को बदलने की सलाह नहीं देता।", category
    if language == "fr":
        return "Je peux expliquer les sujets de santé avec des mots simples.\n\n" + en + "\n\nJe ne pose pas de diagnostic et je ne recommande pas de modifier un traitement prescrit.", category
    return en, category


def _model_answer(message: str, language: str) -> str | None:
    # Accept both the NUVYRA-specific variable and the conventional OpenAI name.
    api_key = (
        os.getenv("NUVYRA_DOCUMENT_AI_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", "").strip()
    )
    base_url = (
        os.getenv("NUVYRA_DOCUMENT_AI_BASE_URL", "https://api.openai.com/v1").strip()
        or "https://api.openai.com/v1"
    ).rstrip("/")
    model = os.getenv("NUVYRA_DOCUMENT_AI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
    if not api_key:
        return None

    language_name = {"en": "English", "hi": "Hindi", "fr": "French"}.get(language, "English")
    system = f"""You are NUVYRA Companion, a broad health-information assistant. Answer the user's actual question directly in {language_name}. Use plain language suitable for someone with no medical background. You may explain general healthcare, symptoms, conditions, anatomy, medicines, tests, reports, prevention, nutrition, sleep, exercise, mental wellbeing, and NUVYRA measurements. Explain rather than diagnose. Never claim certainty that a user has or does not have a disease. Never prescribe, stop, or change a medicine or dose. If a question describes an emergency or severe/rapidly worsening symptoms, advise urgent professional care. For personal NUVYRA results, use only data explicitly supplied in the conversation or application context; never invent measurements. Explain NUVYRA voice/speech, facial dynamics, eye/blinking, gait/movement, breathing, head movement, data quality, personal baseline, multimodal fusion, longitudinal trends and AI analysis as experimental research signals, not clinically validated diagnoses. If the user asks a normal healthcare question, answer that healthcare question instead of redirecting them to NUVYRA. Keep answers focused and useful."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    }
    try:
        with httpx.Client(timeout=25.0) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            return content.strip() if isinstance(content, str) and content.strip() else None
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        return None


def answer(message: str, language: str = "en") -> tuple[str, str, str]:
    category = _category(message)
    text = _model_answer(message, language)
    if text is None:
        text, category = _fallback(message, language)
    return text, category, SYSTEM_DISCLAIMER
