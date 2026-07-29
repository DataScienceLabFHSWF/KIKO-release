from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.services import course_upload_job_service
from app.services.course_upload_job_service import (
    CourseUploadJob,
    CourseUploadJobManager,
)


def _job(
    job_id: str,
    status: str,
    updated_at: datetime,
) -> CourseUploadJob:
    return CourseUploadJob(
        job_id=job_id,
        user_id=1,
        file_name=f"{job_id}.pdf",
        status=status,
        created_at=updated_at,
        updated_at=updated_at,
    )


@pytest.mark.asyncio
async def test_pruning_removes_expired_and_excess_final_jobs_only() -> None:
    now = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)
    manager = CourseUploadJobManager(
        max_retained_final_jobs=2,
        final_job_retention=timedelta(minutes=30),
    )
    jobs = [
        _job("expired", "completed", now - timedelta(minutes=31)),
        _job("oldest-retained", "failed", now - timedelta(minutes=20)),
        _job("cancelled", "cancelled", now - timedelta(minutes=10)),
        _job("completed", "completed", now - timedelta(minutes=5)),
        _job("queued", "queued", now - timedelta(days=1)),
        _job("processing", "processing", now - timedelta(days=1)),
        _job("cancelling", "cancelling", now - timedelta(days=1)),
    ]
    manager._jobs = {job.job_id: job for job in jobs}

    await manager._prune_final_jobs(now=now)

    assert set(manager._jobs) == {
        "cancelled",
        "completed",
        "queued",
        "processing",
        "cancelling",
    }


@pytest.mark.asyncio
async def test_job_completion_prunes_and_clears_task(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    now = datetime.now(timezone.utc)
    manager = CourseUploadJobManager(
        max_retained_final_jobs=1,
        final_job_retention=timedelta(days=1),
    )
    old_job = _job("old-completed", "completed", now - timedelta(minutes=5))
    manager._jobs[old_job.job_id] = old_job

    existing_path = tmp_path / "existing.pdf"
    existing_path.write_bytes(b"existing")

    class FakeSessionContext:
        async def __aenter__(self):
            return object()

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(
        course_upload_job_service,
        "AsyncSessionLocal",
        FakeSessionContext,
    )
    monkeypatch.setattr(
        course_upload_job_service,
        "canonical_storage_path",
        lambda _content_hash: str(existing_path),
    )
    monkeypatch.setattr(
        course_upload_job_service,
        "get_doc_by_hash_name",
        AsyncMock(return_value=object()),
    )

    job = await manager.start_pdf_job(
        user_id=1,
        file_name="new.pdf",
        file_bytes=b"pdf",
        embedding_model_name="embedding-model",
        llm_model_name="llm-model",
        response_language="en",
        qa_count=1,
        quiz_question_count=1,
        quiz_option_count=2,
        misconception_count=1,
    )
    task = job.task

    assert task is not None
    await task

    assert job.status == "completed"
    assert job.task is None
    assert old_job.job_id not in manager._jobs
    assert manager._jobs[job.job_id] is job
