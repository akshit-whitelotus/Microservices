"""
Regression tests for the upload filename handling fix in
app/services/document_service.py.

These call `DocumentService.create_upload` directly (bypassing the
HTTP layer) rather than the `/documents/marks-upload` endpoint. Going
through the endpoint would also schedule `process_document` as a
background task, which reaches out to the AI service and
student-service over the network -- unnecessary and flaky for a test
that's only about how the uploaded bytes get named and stored on
disk.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio

from app.core.config import settings
from app.services.document_service import DocumentService


pytestmark = pytest.mark.asyncio


async def _upload(db_session, filename: str, content: bytes = b"hello world"):

    service = DocumentService()

    return await service.create_upload(
        db=db_session,
        uploaded_by=1,
        filename=filename,
        content_type="text/plain",
        file_content=content,
    )


@pytest_asyncio.fixture
async def db_session():
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------------------------------------
# Path traversal / arbitrary write
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "malicious_filename",
    [
        "/etc/cron.d/evil",
        "../../../etc/passwd",
        "....//....//etc/shadow",
        "..",
    ],
)
async def test_upload_filename_cannot_escape_upload_dir(
    db_session, malicious_filename, isolated_upload_dir
):

    document = await _upload(db_session, malicious_filename)

    stored_path = Path(document.file_path).resolve()
    upload_dir = Path(settings.UPLOAD_DIR).resolve()

    # The stored file must live inside the configured upload
    # directory -- not at the traversal target.
    assert upload_dir in stored_path.parents

    # The file was actually written where the DB row says it was.
    assert stored_path.exists()
    assert stored_path.read_bytes() == b"hello world"

    # The original (untrusted) filename is preserved for display,
    # but never used verbatim as the on-disk path.
    assert document.filename == malicious_filename
    assert str(stored_path) != str(upload_dir / malicious_filename)


async def test_upload_filename_empty_string_still_produces_safe_path(
    db_session, isolated_upload_dir
):

    document = await _upload(db_session, "")

    stored_path = Path(document.file_path).resolve()
    upload_dir = Path(settings.UPLOAD_DIR).resolve()

    assert upload_dir in stored_path.parents
    assert stored_path.exists()


# ---------------------------------------------------------
# Filename collisions
# ---------------------------------------------------------

async def test_duplicate_original_filenames_do_not_overwrite_each_other(
    db_session, isolated_upload_dir
):

    first = await _upload(db_session, "marks.pdf", content=b"first upload")
    second = await _upload(db_session, "marks.pdf", content=b"second upload")

    assert first.file_path != second.file_path

    first_path = Path(first.file_path)
    second_path = Path(second.file_path)

    assert first_path.exists()
    assert second_path.exists()

    # Neither upload clobbered the other's content.
    assert first_path.read_bytes() == b"first upload"
    assert second_path.read_bytes() == b"second upload"

    # Both still report the same original filename for display.
    assert first.filename == second.filename == "marks.pdf"
