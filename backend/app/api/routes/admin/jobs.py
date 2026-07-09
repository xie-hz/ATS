"""Admin job management."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permissions
from app.models import (
    JobCreate,
    JobPublic,
    JobsPublic,
    JobStatus,
    JobUpdate,
    Message,
    User,
)
from app.services import job_service

router = APIRouter(prefix="/admin/jobs", tags=["admin-jobs"])


@router.get("/", response_model=JobsPublic)
def list_jobs(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_READ))],
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
    status: JobStatus | None = None,
) -> Any:
    return job_service.list_jobs(
        session=session,
        user=current_user,
        skip=skip,
        limit=limit,
        keyword=keyword,
        job_status=status,
    )


@router.post("/", response_model=JobPublic)
def create_job(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_CREATE))],
    job_in: JobCreate,
) -> Any:
    job = job_service.create_job(session=session, user=current_user, job_in=job_in)
    return JobPublic.model_validate(job)


@router.get("/{job_id}", response_model=JobPublic)
def get_job(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_READ))],
    job_id: uuid.UUID,
) -> Any:
    job = job_service.get_job(session=session, user=current_user, job_id=job_id)
    return JobPublic.model_validate(job)


@router.patch("/{job_id}", response_model=JobPublic)
def update_job(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_CREATE))],
    job_id: uuid.UUID,
    job_in: JobUpdate,
) -> Any:
    job = job_service.update_job(
        session=session, user=current_user, job_id=job_id, job_in=job_in
    )
    return JobPublic.model_validate(job)


@router.post("/{job_id}/publish", response_model=JobPublic)
def publish_job(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_PUBLISH))],
    job_id: uuid.UUID,
) -> Any:
    job = job_service.publish_job(session=session, user=current_user, job_id=job_id)
    return JobPublic.model_validate(job)


@router.post("/{job_id}/close", response_model=JobPublic)
def close_job(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_CLOSE))],
    job_id: uuid.UUID,
) -> Any:
    job = job_service.close_job(session=session, user=current_user, job_id=job_id)
    return JobPublic.model_validate(job)


@router.post("/{job_id}/reopen", response_model=JobPublic)
def reopen_job(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_PUBLISH))],
    job_id: uuid.UUID,
) -> Any:
    job = job_service.reopen_job(session=session, user=current_user, job_id=job_id)
    return JobPublic.model_validate(job)


@router.delete("/{job_id}", response_model=Message)
def delete_job(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.JOB_CLOSE))],
    job_id: uuid.UUID,
) -> Any:
    job_service.delete_job(session=session, user=current_user, job_id=job_id)
    return Message(message="Job deleted successfully")
