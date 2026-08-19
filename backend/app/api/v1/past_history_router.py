"""Past history, privacy-aware document intelligence and reminders.

Document analysis is organizational research assistance only. It does not
interpret results diagnostically, prescribe treatment, or decide that a test
is medically necessary.
"""
from datetime import date, timedelta
from io import BytesIO
from typing import Optional
import json
import re
import uuid
import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.models import User, PastHistoryRecord, MedicalDocument, HealthReminder
from app.db.session import get_db

router = APIRouter(prefix="/past-history", tags=["Past History & Documents"])
MAX_FILE_BYTES = 12 * 1024 * 1024
TEST_PATTERNS = {
    "CBC / blood count": r"\b(cbc|complete blood count|full blood count|hemogram)\b",
    "BCR-ABL / molecular test": r"\b(bcr[- ]?abl|pcr|molecular)\b",
    "liver function test": r"\b(lft|liver function|ast|alt|bilirubin)\b",
    "kidney function test": r"\b(kft|kidney function|creatinine|urea)\b",
    "thyroid test": r"\b(tsh|thyroid|t3|t4)\b",
    "blood sugar test": r"\b(glucose|blood sugar|hba1c|a1c)\b",
    "lipid profile": r"\b(lipid profile|cholesterol|triglyceride|hdl|ldl)\b",
    "urine test": r"\b(urinalysis|urine routine|urine examination)\b",
}


def _extract_text(data: bytes, mime: str, filename: str) -> str:
    if mime == "application/pdf" or filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            return "\n".join((p.extract_text() or "") for p in PdfReader(BytesIO(data)).pages).strip()[:200_000]
        except Exception:
            return ""
    if mime.startswith("text/") or filename.lower().endswith((".txt", ".csv")):
        return data.decode("utf-8", errors="ignore")[:200_000]
    # Optional OCR: if deployment supplies pytesseract + Pillow, image documents
    # become readable; otherwise the user is told that manual review is needed.
    if mime.startswith("image/"):
        try:
            from PIL import Image
            import pytesseract
            return pytesseract.image_to_string(Image.open(BytesIO(data)))[:200_000].strip()
        except Exception:
            return ""
    return ""


def _rule_analysis(text: str, document_type: str) -> dict:
    lower = text.lower()
    tests = [name for name, pattern in TEST_PATTERNS.items() if re.search(pattern, lower)]
    medication_lines = [line.strip()[:300] for line in text.splitlines() if re.search(r"\b(tablet|capsule|mg|mcg|ml|once daily|twice daily|morning|evening|dose)\b", line, re.I)][:30]
    dates = re.findall(r"\b(?:20\d{2}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]20\d{2})\b", text)
    return {"document_type": document_type, "text_extracted": bool(text.strip()), "detected_tests": tests, "possible_medication_lines": medication_lines, "dates_found": dates[:20]}


async def _ai_analysis(text: str, document_type: str) -> Optional[dict]:
    """Optional LLM analysis with a strict, non-diagnostic contract.

    If NUVYRA_DOCUMENT_AI_API_KEY and NUVYRA_DOCUMENT_AI_BASE_URL are absent,
    the deterministic extractor remains the safe fallback.
    """
    key = __import__("os").getenv("NUVYRA_DOCUMENT_AI_API_KEY")
    base = __import__("os").getenv("NUVYRA_DOCUMENT_AI_BASE_URL", "https://api.openai.com/v1")
    model = __import__("os").getenv("NUVYRA_DOCUMENT_AI_MODEL", "gpt-4.1-mini")
    if not key or not text.strip(): return None
    prompt = f"""You are NUVYRA's document-organization assistant. Analyze this {document_type} only for organization. Return JSON with keys: summary (short plain-language description of what the document contains), medications (array of objects with name, dose, frequency only when explicitly readable), mentioned_tests (array), dates (array), follow_up_mentions (array of text that explicitly mention follow-up/repeat testing), uncertainty_notes (array). Never diagnose, infer a disease, interpret a lab result as normal/abnormal, recommend treatment, or invent missing values. If unclear, say unclear. Document text:\n{text[:120000]}"""
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.post(f"{base.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json={"model": model, "temperature": 0, "response_format": {"type": "json_object"}, "messages":[{"role":"system","content":"Return only valid JSON. Do not make medical decisions."},{"role":"user","content":prompt}]})
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            result = json.loads(content)
            if isinstance(result, dict): return result
    except Exception:
        return None
    return None


@router.get("")
def get_past_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = db.scalars(select(PastHistoryRecord).where(PastHistoryRecord.user_id == current_user.id).order_by(PastHistoryRecord.created_at.desc())).all()
    documents = db.scalars(select(MedicalDocument).where(MedicalDocument.user_id == current_user.id).order_by(MedicalDocument.uploaded_at.desc())).all()
    reminders = db.scalars(select(HealthReminder).where(HealthReminder.user_id == current_user.id, HealthReminder.completed.is_(False)).order_by(HealthReminder.due_date.asc().nullslast())).all()
    return {"history":[{"id":str(x.id),"illness_name":x.illness_name,"details":x.details,"diagnosed_on":x.diagnosed_on.isoformat() if x.diagnosed_on else None,"current_status":x.current_status} for x in history],"documents":[{"id":str(x.id),"type":x.document_type,"filename":x.filename,"analysis":x.analysis,"uploaded_at":x.uploaded_at.isoformat()} for x in documents],"reminders":[{"id":str(x.id),"title":x.title,"message":x.message,"due_date":x.due_date.isoformat() if x.due_date else None} for x in reminders]}


@router.post("/illness", status_code=201)
def add_history(illness_name: str = Form(...), details: Optional[str] = Form(None), diagnosed_on: Optional[date] = Form(None), current_status: Optional[str] = Form(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not illness_name.strip(): raise HTTPException(400, "Please provide a history item.")
    item=PastHistoryRecord(user_id=current_user.id,illness_name=illness_name.strip(),details=details,diagnosed_on=diagnosed_on,current_status=current_status)
    db.add(item); db.commit(); db.refresh(item); return {"id":str(item.id),"message":"Past history saved."}


@router.post("/documents", status_code=201)
async def upload_medical_document(document_type: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data=await file.read()
    if not data: raise HTTPException(400,"The uploaded file is empty.")
    if len(data)>MAX_FILE_BYTES: raise HTTPException(413,"File is too large. Maximum size is 12 MB.")
    mime=file.content_type or "application/octet-stream"; filename=file.filename or "document"
    text=_extract_text(data,mime,filename); analysis=_rule_analysis(text,document_type); ai_result=await _ai_analysis(text,document_type)
    if ai_result: analysis["ai_analysis"]={**ai_result,"engine":"optional configured document AI","non_diagnostic":True}
    else: analysis["ai_analysis"]={"engine":"local document intelligence","non_diagnostic":True,"note":"No external AI model was configured or the document was not text-readable; rule-based extraction was used."}
    if not text: analysis["review_note"]="No readable text was extracted. Review the original document manually; for image scans, enable the optional OCR dependencies in the deployment."
    else: analysis["review_note"]="Extracted information is for organization and reminders. Review the original document and confirm medical decisions with a clinician."
    doc=MedicalDocument(user_id=current_user.id,document_type=document_type,filename=filename,mime_type=mime,extracted_text=text[:200_000] or None,analysis=analysis)
    db.add(doc); db.flush()
    mentioned=set(analysis.get("detected_tests",[])) | set((analysis.get("ai_analysis") or {}).get("mentioned_tests",[]))
    if document_type.lower()=="prescription":
        for test in sorted(mentioned):
            db.add(HealthReminder(user_id=current_user.id,title=f"Check report: {test}",message=f"Your uploaded document mentions {test}. If your clinician asked you to complete this, upload the latest result so NUVYRA can keep your record organized.",due_date=date.today()+timedelta(days=30),source_document_id=doc.id))
    elif document_type.lower() in {"report","lab_report","test_report"}:
        for reminder in db.scalars(select(HealthReminder).where(HealthReminder.user_id==current_user.id,HealthReminder.completed.is_(False))).all():
            if reminder.title.replace("Check report: ","") in mentioned: reminder.completed=True
    db.commit(); db.refresh(doc)
    return {"id":str(doc.id),"filename":doc.filename,"analysis":analysis,"reminders_created":sorted(mentioned) if document_type.lower()=="prescription" else []}


@router.post("/reminders/{reminder_id}/complete")
def complete_reminder(reminder_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reminder=db.scalar(select(HealthReminder).where(HealthReminder.id==reminder_id,HealthReminder.user_id==current_user.id))
    if not reminder: raise HTTPException(404,"Reminder not found.")
    reminder.completed=True; db.commit(); return {"message":"Reminder completed."}
