"""Past medical history, document analysis and test reminders."""
from datetime import date, timedelta
from io import BytesIO
from typing import Optional
import re
import uuid
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
}

def _extract_text(data: bytes, mime: str, filename: str) -> str:
    if mime == "application/pdf" or filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(data))
            return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        except Exception:
            return ""
    if mime.startswith("text/") or filename.lower().endswith((".txt", ".csv")):
        return data.decode("utf-8", errors="ignore")[:200_000]
    return ""

def _analyze_document(text: str, document_type: str) -> dict:
    lower = text.lower()
    detected_tests = [name for name, pattern in TEST_PATTERNS.items() if re.search(pattern, lower)]
    medication_lines = [line.strip()[:300] for line in text.splitlines() if re.search(r"\b(tablet|capsule|mg|mcg|ml|once daily|twice daily|morning|evening|dose)\b", line, re.I)][:30]
    dates = re.findall(r"\b(?:20\d{2}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]20\d{2})\b", text)
    return {"document_type": document_type, "text_extracted": bool(text.strip()), "detected_tests": detected_tests, "possible_medication_lines": medication_lines, "dates_found": dates[:20], "review_note": "Computer extraction is for organization and reminders only. Check the original document and confirm medical decisions with a clinician."}

@router.get("")
def get_past_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history = db.scalars(select(PastHistoryRecord).where(PastHistoryRecord.user_id == current_user.id).order_by(PastHistoryRecord.created_at.desc())).all()
    documents = db.scalars(select(MedicalDocument).where(MedicalDocument.user_id == current_user.id).order_by(MedicalDocument.uploaded_at.desc())).all()
    reminders = db.scalars(select(HealthReminder).where(HealthReminder.user_id == current_user.id, HealthReminder.completed.is_(False)).order_by(HealthReminder.due_date.asc().nullslast())).all()
    return {"history": [{"id": str(x.id), "illness_name": x.illness_name, "details": x.details, "diagnosed_on": x.diagnosed_on.isoformat() if x.diagnosed_on else None, "current_status": x.current_status} for x in history], "documents": [{"id": str(x.id), "type": x.document_type, "filename": x.filename, "analysis": x.analysis, "uploaded_at": x.uploaded_at.isoformat()} for x in documents], "reminders": [{"id": str(x.id), "title": x.title, "message": x.message, "due_date": x.due_date.isoformat() if x.due_date else None} for x in reminders]}

@router.post("/illness", status_code=201)
def add_history(illness_name: str = Form(...), details: Optional[str] = Form(None), diagnosed_on: Optional[date] = Form(None), current_status: Optional[str] = Form(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = PastHistoryRecord(user_id=current_user.id, illness_name=illness_name.strip(), details=details, diagnosed_on=diagnosed_on, current_status=current_status)
    db.add(item); db.commit(); db.refresh(item)
    return {"id": str(item.id), "message": "Past history saved."}

@router.post("/documents", status_code=201)
async def upload_medical_document(document_type: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = await file.read()
    if not data: raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > MAX_FILE_BYTES: raise HTTPException(413, "File is too large. Maximum size is 12 MB.")
    mime = file.content_type or "application/octet-stream"
    text = _extract_text(data, mime, file.filename or "document")
    analysis = _analyze_document(text, document_type)
    doc = MedicalDocument(user_id=current_user.id, document_type=document_type, filename=file.filename or "document", mime_type=mime, extracted_text=text[:200_000] or None, analysis=analysis)
    db.add(doc); db.flush()
    if document_type.lower() == "prescription":
        for test in analysis["detected_tests"]:
            db.add(HealthReminder(user_id=current_user.id, title=f"Check report: {test}", message=f"Your uploaded prescription/document mentions {test}. If your clinician asked you to complete this test, upload the latest result so NUVYRA can keep your record organized.", due_date=date.today() + timedelta(days=30), source_document_id=doc.id))
    elif document_type.lower() in {"report", "lab_report", "test_report"}:
        for reminder in db.scalars(select(HealthReminder).where(HealthReminder.user_id == current_user.id, HealthReminder.completed.is_(False))).all():
            test_name = reminder.title.replace("Check report: ", "")
            if test_name in analysis["detected_tests"]: reminder.completed = True
    db.commit(); db.refresh(doc)
    return {"id": str(doc.id), "filename": doc.filename, "analysis": analysis, "reminders_created": analysis["detected_tests"] if document_type.lower() == "prescription" else []}

@router.post("/reminders/{reminder_id}/complete")
def complete_reminder(reminder_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reminder = db.scalar(select(HealthReminder).where(HealthReminder.id == reminder_id, HealthReminder.user_id == current_user.id))
    if not reminder: raise HTTPException(404, "Reminder not found.")
    reminder.completed = True; db.commit()
    return {"message": "Reminder completed."}
