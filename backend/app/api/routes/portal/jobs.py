"""Portal public job browsing (no auth)."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models import JobPublic, JobsPublic
from app.services import portal_service

router = APIRouter(prefix="/portal/jobs", tags=["portal-jobs"])


@router.get("/", response_model=JobsPublic)
def list_portal_jobs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
) -> Any:
    return portal_service.list_portal_jobs(
        session=session, skip=skip, limit=limit, keyword=keyword
    )


@router.get("/{job_id}", response_model=JobPublic)
def get_portal_job(session: SessionDep, job_id: uuid.UUID) -> Any:
    job = portal_service.get_portal_job(session=session, job_id=job_id)
    return JobPublic.model_validate(job)
