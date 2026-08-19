"""Safe conversational companion for system and general health questions."""
import re
from typing import Tuple


SYSTEM_DISCLAIMER = (
    "NUVYRA is a research platform. Its digital-biomarker features and stability index "
    "are experimental and are not clinically validated or a diagnosis."
)


def _answer_en(message: str) -> Tuple[str, str]:
    q = message.lower().strip()
    if any(k in q for k in ("what is nuvyra", "what does this system", "how does this work", "how it works")):
        return ("NUVYRA collects everyday voice, face, eye, movement, head and breathing-related research signals, checks their quality, compares them with your own history, and explains changes over time. It is designed for research and personal pattern awareness, not diagnosis.", "system")
    if any(k in q for k in ("accuracy", "accurate", "reliable")):
        return ("The current measurements are research-level estimates. Accuracy depends on the feature, recording quality, data and validation set. NUVYRA should not be treated as clinically validated.", "research")
    if any(k in q for k in ("baseline", "usual", "normal for me")):
        return ("Your personal baseline is built from your previous usable check-ins. NUVYRA compares a new session with that pattern instead of assuming one universal value is ideal for everyone.", "research")
    if any(k in q for k in ("doctor", "diagnos", "disease", "illness", "medicine", "medication", "symptom", "pain", "treatment", "am i healthy", "cancer")):
        return ("I can explain health concepts and help you understand what NUVYRA displays, but I cannot diagnose a condition, decide whether a symptom is caused by an illness, or recommend treatment. If you are worried about a health problem, please speak with a qualified healthcare professional.", "health")
    if any(k in q for k in ("emergency", "urgent", "can't breathe", "severe", "fainting")):
        return ("If you are experiencing a severe or rapidly worsening health problem, seek urgent medical care rather than relying on NUVYRA. I can help explain the software, but I cannot provide emergency assessment.", "safety")
    return ("I can help explain NUVYRA, its measurements, personal baselines, trends, AI analysis, past-history documents, reminders, and general health concepts. Tell me what you would like to understand.", "system")


def answer(message: str, language: str = "en") -> tuple[str, str, str]:
    # Keep multilingual support deterministic even when no external LLM is configured.
    text, category = _answer_en(message)
    if language == "hi":
        text = "मैं NUVYRA, उसके measurements, personal baseline, trends, AI analysis और सामान्य health concepts समझाने में मदद कर सकता हूँ। मैं diagnosis या treatment की सलाह नहीं देता। आप क्या समझना चाहते हैं?" if category == "system" and text.startswith("I can help") else text
    elif language == "fr":
        text = "Je peux expliquer NUVYRA, ses mesures, votre référence personnelle, les tendances et son analyse IA. Je ne peux pas établir de diagnostic ni recommander un traitement. Que souhaitez-vous comprendre ?" if category == "system" and text.startswith("I can help") else text
    return text, category, SYSTEM_DISCLAIMER
