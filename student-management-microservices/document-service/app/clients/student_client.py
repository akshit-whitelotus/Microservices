from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class StudentServiceClient:
    """
    Client for student-service internal APIs.
    """


    def __init__(self) -> None:

        self.base_url = (
            settings.STUDENT_SERVICE_URL.rstrip("/")
        )

        self.timeout = httpx.Timeout(
            30.0
        )


    # ---------------------------------------------------------
    # Bulk Upsert Grades
    # ---------------------------------------------------------

    async def bulk_upsert_grades(
        self,
        *,
        items: list[dict[str, Any]],
        uploaded_by: int,
        source_document_id: str,
    ) -> dict[str, Any]:
        """
        Send extracted grades to student-service.
        """


        payload = {

            "items": [

                {
                    **item,
                    "uploaded_by":
                        uploaded_by,

                    "source_document_id":
                        source_document_id,
                }

                for item in items

            ]

        }


        headers = {

            "X-Internal-Service-Token":
                settings.INTERNAL_SERVICE_TOKEN,

            "Content-Type":
                "application/json",

        }


        url = (
            f"{self.base_url}"
            "/internal/v1/grades/bulk-upsert"
        )


        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:


            response = await client.post(
                url,
                json=payload,
                headers=headers,
            )


            if response.status_code >= 400:

                logger.error(
                    "Student service bulk upload failed",
                    extra={
                        "status_code":
                            response.status_code,

                        "response":
                            response.text,
                    },
                )


                response.raise_for_status()



            return response.json()