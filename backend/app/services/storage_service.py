import hashlib
import json
import math
import struct
import uuid
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.file_upload import FileUploadRecord


class StorageService:
    ALLOWED_EXTENSIONS = {
        "voice": {".wav", ".mp3", ".m4a", ".ogg", ".webm"},
        "video": {".mp4", ".webm", ".avi", ".mov"},
        "image": {".jpg", ".jpeg", ".png", ".webp"},
        "pdf_report": {".pdf"},
    }
    MAX_FILE_SIZE = 50 * 1024 * 1024

    def __init__(self, db: Session, upload_dir: str = "uploads"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def analyze_bytes(data: bytes, category: str, filename: str, mime: str, path: Path) -> dict[str, Any]:
        ext = Path(filename).suffix.lower()
        if category == "pdf_report" or ext == ".pdf":
            try:
                from pypdf import PdfReader
                pages = PdfReader(BytesIO(data)).pages
                text = "\n".join((page.extract_text() or "") for page in pages).strip()
                return {"method": "pypdf", "pages": len(pages), "text_characters": len(text), "text_preview": text[:5000], "text_extracted": bool(text)}
            except Exception as exc:
                return {"method": "pypdf", "text_extracted": False, "error": str(exc)}
        if category == "image" or mime.startswith("image/"):
            try:
                from PIL import Image, ImageStat
                image = Image.open(BytesIO(data)).convert("RGB")
                stat = ImageStat.Stat(image)
                return {"method": "Pillow", "width": image.width, "height": image.height, "channels": 3, "mean_rgb": [round(x, 3) for x in stat.mean], "mean_luminance": round(sum(stat.mean) / 3, 3)}
            except Exception as exc:
                return {"method": "Pillow", "error": str(exc)}
        if category == "voice" and ext == ".wav":
            try:
                import wave
                with wave.open(BytesIO(data), "rb") as wav:
                    channels, rate, frames, width = wav.getnchannels(), wav.getframerate(), wav.getnframes(), wav.getsampwidth()
                    raw = wav.readframes(min(frames, rate * 60))
                if width != 2 or not raw:
                    return {"method": "wave", "sample_rate_hz": rate, "channels": channels, "duration_seconds": round(frames / rate, 3)}
                samples = struct.unpack("<" + "h" * (len(raw) // 2), raw)
                rms = math.sqrt(sum(s * s for s in samples) / max(len(samples), 1)) / 32768
                crossings = sum(1 for a, b in zip(samples, samples[1:]) if (a < 0 <= b) or (a >= 0 > b))
                return {"method": "PCM waveform", "sample_rate_hz": rate, "channels": channels, "duration_seconds": round(frames / rate, 3), "rms_amplitude": round(rms, 6), "zero_crossing_rate": round(crossings / max(len(samples) - 1, 1), 6)}
            except Exception as exc:
                return {"method": "wave", "error": str(exc)}
        if category == "video":
            try:
                import cv2
                cap = cv2.VideoCapture(str(path))
                fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
                frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
                cap.release()
                return {"method": "OpenCV", "fps": round(fps, 3), "frame_count": frames, "duration_seconds": round(frames / fps, 3) if fps else None, "width": width, "height": height}
            except Exception as exc:
                return {"method": "OpenCV", "error": str(exc), "note": "Install opencv-python-headless for video extraction."}
        return {"method": "metadata", "format": ext.lstrip(".") or mime, "bytes": len(data), "note": "Stored successfully; detailed extraction is not available for this format in the current runtime."}

    async def save_upload(self, file: UploadFile, patient_id: uuid.UUID, file_category: str, user_id: uuid.UUID) -> FileUploadRecord:
        if file_category not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file category '{file_category}'. Allowed: {list(self.ALLOWED_EXTENSIONS)}")
        ext = Path(file.filename or "").suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS[file_category]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File extension '{ext}' not permitted for category '{file_category}'.")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty.")
        if len(data) > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File size exceeds maximum allowed limit of 50 MB.")

        filename = file.filename or "uploaded_file"
        mime = file.content_type or "application/octet-stream"
        stored_filename = f"{patient_id}_{file_category}_{uuid.uuid4().hex[:8]}{ext}"
        directory = self.upload_dir / file_category
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / stored_filename
        path.write_bytes(data)
        analysis = self.analyze_bytes(data, file_category, filename, mime, path)
        notes = json.dumps({"version": 1, "status": "analyzed", "analysis": analysis}, ensure_ascii=False)

        record = FileUploadRecord(patient_id=patient_id, file_category=file_category, original_filename=filename, stored_filename=stored_filename, file_path=str(path), file_size_bytes=len(data), mime_type=mime, sha256_checksum=hashlib.sha256(data).hexdigest(), processing_status="COMPLETED", notes=notes, uploaded_by_user_id=user_id)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
