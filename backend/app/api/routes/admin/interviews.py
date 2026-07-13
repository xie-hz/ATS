"""Admin interview management: schedule, calendar, feedback."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permissions
from app.models import (
    BatchInterviewCreate,
    BatchInterviewResult,
    FeedbackCreate,
    FeedbackPublic,
    InterviewCreate,
    InterviewPublic,
    InterviewsPublic,
    InterviewStatus,
    InterviewUpdate,
    User,
)
from app.services import interview_service

router = APIRouter(prefix="/admin/interviews", tags=["admin-interviews"])


@router.get("/calendar", response_model=list[InterviewPublic])
def list_calendar(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.INTERVIEW_READ))],
) -> Any:
    return interview_service.list_calendar(session=session, user=current_user)


@router.get("/", response_model=InterviewsPublic)
def list_interviews(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.INTERVIEW_READ))],
    skip: int = 0,
    limit: int = 100,
    status: InterviewStatus | None = None,
) -> Any:
    return interview_service.list_interviews(
        session=session,
        user=current_user,
        skip=skip,
        limit=limit,
        interview_status=status,
    )


@router.post(
    "/",
    response_model=InterviewPublic,
    dependencies=[Depends(require_permission(Permissions.INTERVIEW_CREATE))],
)
def create_interview(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.INTERVIEW_CREATE))],
    interview_in: InterviewCreate,
) -> Any:
    iv = interview_service.create_interview(
        session=session, interview_in=interview_in, host_email=current_user.email
    )
    return InterviewPublic.model_validate(iv)


@router.post(
    "/batch",
    response_model=BatchInterviewResult,
    dependencies=[Depends(require_permission(Permissions.INTERVIEW_CREATE))],
)
def batch_create_interviews(
    session: SessionDep,
    batch_in: BatchInterviewCreate,
) -> Any:
    """§16 batch invite: schedule one interview per selected application."""
    return interview_service.batch_create_interviews(
        session=session, batch_in=batch_in
    )


@router.get("/{interview_id}", response_model=InterviewPublic)
def get_interview(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.INTERVIEW_READ))],
    interview_id: uuid.UUID,
) -> Any:
    iv = interview_service.get_interview(
        session=session, user=current_user, interview_id=interview_id
    )
    return interview_service.to_public(session=session, iv=iv)


@router.get(
    "/{interview_id}/feedback",
    response_model=FeedbackPublic,
    dependencies=[Depends(require_permission(Permissions.INTERVIEW_READ))],
)
def get_feedback(
    session: SessionDep,
    interview_id: uuid.UUID,
) -> Any:
    fb = interview_service.get_feedback(session=session, interview_id=interview_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return FeedbackPublic.model_validate(fb)


@router.patch("/{interview_id}", response_model=InterviewPublic)
def update_interview(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.INTERVIEW_CREATE))],
    interview_id: uuid.UUID,
    body: InterviewUpdate,
) -> Any:
    """Update a scheduled interview (time, interviewer, round)."""
    iv = interview_service.update_interview(
        session=session,
        user=current_user,
        interview_id=interview_id,
        interviewer_id=body.interviewer_id,
        scheduled_time=body.scheduled_time,
        round=body.round,
    )
    return InterviewPublic.model_validate(iv)


@router.post("/{interview_id}/cancel", response_model=InterviewPublic)
def cancel_interview(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.INTERVIEW_CREATE))],
    interview_id: uuid.UUID,
) -> Any:
    iv = interview_service.cancel_interview(
        session=session, user=current_user, interview_id=interview_id
    )
    return InterviewPublic.model_validate(iv)


@router.post("/{interview_id}/feedback", response_model=FeedbackPublic)
def submit_feedback(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.FEEDBACK_CREATE))],
    interview_id: uuid.UUID,
    feedback_in: FeedbackCreate,
) -> Any:
    feedback = interview_service.submit_feedback(
        session=session,
        user=current_user,
        interview_id=interview_id,
        feedback_in=feedback_in,
    )
    return FeedbackPublic.model_validate(feedback)
