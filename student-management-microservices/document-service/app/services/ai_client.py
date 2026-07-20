from __future__ import annotations

import json
import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


PROMPT_VERSION = "v1"



class AIClient:


    async def extract_grades(
        self,
        text: str,
    ) -> list[dict]:

        prompt = f"""
You are extracting student marks.

Return ONLY valid JSON.

No markdown.
No explanation.

Format:

[
 {{
  "student_id": 1,
  "subject": "Math",
  "marks": 80,
  "max_marks":100,
  "exam_term":"Mid Term"
 }}
]

Prompt Version:
{PROMPT_VERSION}

Document:

{text}
"""


        timeout = httpx.Timeout(
            30.0
        )


        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:

            response = await client.post(
                settings.AI_API_URL,
                headers={
                    "Authorization":
                    f"Bearer {settings.AI_API_KEY}"
                },
                json={
                    "prompt": prompt
                },
            )


        response.raise_for_status()


        raw = response.json()["response"]


        try:

            data = json.loads(raw)


        except json.JSONDecodeError as exc:

            logger.exception(
                "AI returned invalid JSON"
            )

            raise ValueError(
                "AI response was not valid JSON"
            ) from exc


        if not isinstance(
            data,
            list,
        ):

            raise ValueError(
                "AI output must be a list"
            )


        return data