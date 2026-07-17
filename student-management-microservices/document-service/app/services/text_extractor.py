from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from fastapi import HTTPException


class TextExtractor:
    """
    Extract text from uploaded documents.
    """


    # ---------------------------------------------------------
    # Extract
    # ---------------------------------------------------------

    def extract(
        self,
        file_path: str,
        content_type: str,
    ) -> str:
        """
        Extract raw text from PDF/TXT.
        """


        if content_type == "application/pdf":

            return self._extract_pdf(
                file_path
            )


        if content_type == "text/plain":

            return self._extract_txt(
                file_path
            )


        raise HTTPException(
            status_code=422,
            detail="Unsupported document type",
        )


    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    def _extract_pdf(
        self,
        file_path: str,
    ) -> str:

        reader = PdfReader(
            file_path
        )

        pages: list[str] = []


        for page in reader.pages:

            text = page.extract_text()

            if text:

                pages.append(
                    text
                )


        return "\n".join(
            pages
        )


    # ---------------------------------------------------------
    # TXT
    # ---------------------------------------------------------

    def _extract_txt(
        self,
        file_path: str,
    ) -> str:


        return Path(
            file_path
        ).read_text(
            encoding="utf-8"
        )