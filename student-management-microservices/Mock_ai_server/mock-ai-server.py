"""
Mock AI API for local testing of document-service's marks-extraction pipeline.

Mimics the exact contract app/services/ai_client.py already expects:
  POST /   body: {"prompt": "<the full prompt text>"}
  ->       {"response": "<JSON-encoded string of extracted rows>"}

It does a simple, deterministic parse of the table-like text produced by
pypdf/pdfplumber for PDFs (or plain comma-separated lines for TXT files) --
no real AI model involved. Good enough to exercise the whole upload ->
extract -> match -> write-to-student-service pipeline end to end.

Run:
    pip install fastapi uvicorn --break-system-packages
    python3 mock_ai_server.py

Then in document-service/.env:
    AI_API_URL=http://127.0.0.1:8099/
    AI_API_KEY=mock-key   (any value -- this server doesn't check it)
"""

from __future__ import annotations

import json
import re

from fastapi import FastAPI, Request

app = FastAPI(title="Mock AI API")


EXAM_TERM_RE = re.compile(r"exam term\s*:\s*(.+)", re.IGNORECASE)
HEADER_TOKENS = ["student_id", "subject", "marks", "max_marks"]


def _extract_document_text(prompt: str) -> str:
    marker = "Document:"
    idx = prompt.find(marker)
    return prompt[idx + len(marker):].strip() if idx != -1 else prompt.strip()


def _parse_pdf_style(lines: list[str]) -> list[dict]:
    """
    Handles pypdf-style extraction where each table cell is its own line,
    in row-major order, e.g.:
        student_id
        subject
        marks
        max_marks
        1
        Data Structures
        78
        100
        2
        ...
    """
    lower = [line.strip().lower() for line in lines]

    header_positions = [lower.index(tok) for tok in HEADER_TOKENS if tok in lower]
    if len(header_positions) != len(HEADER_TOKENS):
        return []

    data_start = max(header_positions) + 1
    data_lines = [line.strip() for line in lines[data_start:] if line.strip()]

    rows = []
    for i in range(0, len(data_lines) - 3, 4):
        chunk = data_lines[i:i + 4]
        try:
            rows.append({
                "student_id": int(chunk[0]),
                "subject": chunk[1],
                "marks": float(chunk[2]),
                "max_marks": float(chunk[3]),
            })
        except (ValueError, IndexError):
            continue
    return rows


def _parse_csv_style(lines: list[str]) -> list[dict]:
    """
    Handles plain TXT files formatted as: student_id,subject,marks,max_marks
    """
    rows = []
    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            continue
        try:
            rows.append({
                "student_id": int(parts[0]),
                "subject": parts[1],
                "marks": float(parts[2]),
                "max_marks": float(parts[3]),
            })
        except ValueError:
            continue
    return rows


@app.get("/")
def health():
    return {"status": "mock AI server is running"}


@app.post("/")
async def extract(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")

    document_text = _extract_document_text(prompt)
    lines = document_text.splitlines()

    exam_term_match = EXAM_TERM_RE.search(document_text)
    exam_term = exam_term_match.group(1).strip() if exam_term_match else "Unspecified Term"

    rows = _parse_pdf_style(lines) or _parse_csv_style(lines)

    for row in rows:
        row["exam_term"] = exam_term

    return {"response": json.dumps(rows)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8099)