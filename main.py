from __future__ import annotations

import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .human_detector import HumanDetector
from .models import AnalysisResponse
from .plagiarism_detector import PlagiarismDetector
from .report_generator import generate_ieee_report
from .text_extractor import extract_text_from_file
from .utils import clean_text, ensure_directory

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BASE_DIR / "corpus"
EMBEDDINGS_FILE = BASE_DIR / "corpus_embeddings.pkl"
REPORTS_DIR = ensure_directory(BASE_DIR / "reports")

app = FastAPI(title="GH Plagiarism Checker API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

plagiarism_detector: PlagiarismDetector | None = None
human_detector: HumanDetector | None = None
report_index: dict[str, Path] = {}


@app.on_event("startup")
def startup_event() -> None:
    global plagiarism_detector, human_detector
    plagiarism_detector = PlagiarismDetector(corpus_dir=CORPUS_DIR, embeddings_file=EMBEDDINGS_FILE)
    human_detector = HumanDetector()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload", response_model=AnalysisResponse)
async def upload_for_analysis(file: UploadFile | None = File(default=None), text: str | None = Form(default=None)):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either a file or text input.")
    if plagiarism_detector is None or human_detector is None:
        raise HTTPException(status_code=500, detail="Models not initialized.")

    raw_text, filename = "", "typed-input.txt"
    if file:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        raw_text = extract_text_from_file(file.filename, content)
        filename = file.filename
    else:
        raw_text = clean_text(text or "")
    if not raw_text:
        raise HTTPException(status_code=400, detail="No readable text found.")

    try:
        plagiarism_percentage, top_sources = plagiarism_detector.analyze(raw_text)
        humanized_percentage, ai_generated_percentage = human_detector.analyze(raw_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    job_id = uuid.uuid4().hex
    report = generate_ieee_report(
        filename=filename,
        input_excerpt=raw_text,
        plagiarism_percentage=plagiarism_percentage,
        humanized_percentage=humanized_percentage,
        ai_generated_percentage=ai_generated_percentage,
        top_sources=top_sources,
    )
    out_path = REPORTS_DIR / f"{job_id}.docx"
    out_path.write_bytes(report.read())
    report_index[job_id] = out_path

    return AnalysisResponse(
        job_id=job_id,
        filename=filename,
        plagiarism_percentage=plagiarism_percentage,
        humanized_percentage=humanized_percentage,
        ai_generated_percentage=ai_generated_percentage,
        top_sources=top_sources,
    )


@app.get("/download-report/{job_id}")
def download_report(job_id: str):
    report_path = report_index.get(job_id)
    if not report_path or not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(
        path=report_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"gh-plagiarism-report-{job_id}.docx",
    )
