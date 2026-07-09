"""Admin candidate management + resume upload (local storage, phase 1)."""

import uuid
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permissions
from app.models import (
    CandidateCreate,
    CandidatePublic,
    CandidatesPublic,
    CandidateUpdate,
    User,
)
from app.services import candidate_service

router = APIRouter(prefix="/admin/candidates", tags=["admin-candidates"])

UPLOAD_DIR = Path("uploads")


@router.get("/", response_model=CandidatesPublic)
def list_candidates(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.CANDIDATE_READ))],
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
    tag: str | None = None,
    source: str | None = None,
) -> Any:
    return candidate_service.list_candidates(
        session=session,
        user=current_user,
        skip=skip,
        limit=limit,
        keyword=keyword,
        tag=tag,
        source=source,
    )


@router.post(
    "/",
    response_model=CandidatePublic,
    dependencies=[Depends(require_permission(Permissions.CANDIDATE_CREATE))],
)
def create_candidate(
    session: SessionDep,
    candidate_in: CandidateCreate,
) -> Any:
    candidate = candidate_service.create_candidate(
        session=session, candidate_in=candidate_in
    )
    return CandidatePublic.model_validate(candidate)


@router.get("/{candidate_id}", response_model=CandidatePublic)
def get_candidate(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.CANDIDATE_READ))],
    candidate_id: uuid.UUID,
) -> Any:
    candidate = candidate_service.get_candidate(
        session=session, user=current_user, candidate_id=candidate_id
    )
    return CandidatePublic.model_validate(candidate)


@router.patch("/{candidate_id}", response_model=CandidatePublic)
def update_candidate(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.CANDIDATE_UPDATE))],
    candidate_id: uuid.UUID,
    candidate_in: CandidateUpdate,
) -> Any:
    candidate = candidate_service.update_candidate(
        session=session,
        user=current_user,
        candidate_id=candidate_id,
        candidate_in=candidate_in,
    )
    return CandidatePublic.model_validate(candidate)


@router.post("/{candidate_id}/resume", response_model=CandidatePublic)
def upload_resume(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.CANDIDATE_UPDATE))],
    candidate_id: uuid.UUID,
    file: UploadFile,
) -> Any:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename_part = (file.filename or "resume").rsplit(".", 1)[-1]
    ext = filename_part if filename_part and "." in (file.filename or "") else "bin"
    filename = f"{candidate_id}_{uuid.uuid4().hex}.{ext}"
    (UPLOAD_DIR / filename).write_bytes(file.file.read())
    candidate = candidate_service.set_resume_url(
        session=session,
        user=current_user,
        candidate_id=candidate_id,
        resume_url=f"/uploads/{filename}",
    )
    return CandidatePublic.model_validate(candidate)
