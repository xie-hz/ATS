"""State machine definitions for ATS entities.

Each state machine is a mapping of `current_state -> {allowed_target_states}`.
`assert_*_transition` validates a proposed transition and raises HTTP 400 if it
is not permitted by the machine.
"""

from enum import Enum
from typing import TypeVar

from fastapi import HTTPException, status

from app.models import (
    ApplicationStage,
    InterviewStatus,
    JobStatus,
    OfferStatus,
)

T = TypeVar("T", bound=Enum)


def _assert_can_transition[T: Enum](
    transitions: dict[T, set[T]], current: T, target: T, entity: str
) -> None:
    allowed = transitions.get(current, set())
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot transition {entity} from {current.value} to "
                f"{target.value}"
            ),
        )


# ---------------------------------------------------------------------------
# Application stage
#   APPLIED -> SCREENING -> INTERVIEW -> OFFER -> HIRED
#   any active stage -> REJECTED
#   REJECTED -> SCREENING (restore)
# ---------------------------------------------------------------------------

APPLICATION_TRANSITIONS: dict[ApplicationStage, set[ApplicationStage]] = {
    ApplicationStage.APPLIED: {ApplicationStage.SCREENING, ApplicationStage.REJECTED},
    ApplicationStage.SCREENING: {
        ApplicationStage.INTERVIEW,
        ApplicationStage.REJECTED,
    },
    ApplicationStage.INTERVIEW: {ApplicationStage.OFFER, ApplicationStage.REJECTED},
    ApplicationStage.OFFER: {ApplicationStage.HIRED, ApplicationStage.REJECTED},
    ApplicationStage.HIRED: {ApplicationStage.SCREENING},  # undo hire
    ApplicationStage.REJECTED: {ApplicationStage.SCREENING},
}


def assert_application_transition(
    current: ApplicationStage, target: ApplicationStage
) -> None:
    _assert_can_transition(
        APPLICATION_TRANSITIONS, current, target, "application"
    )


# ---------------------------------------------------------------------------
# Job status
#   DRAFT -> PENDING_APPROVAL -> OPEN
#   OPEN <-> PAUSED
#   any -> CLOSED (terminal)
# ---------------------------------------------------------------------------

JOB_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.DRAFT: {JobStatus.PENDING_APPROVAL, JobStatus.CLOSED},
    JobStatus.PENDING_APPROVAL: {JobStatus.OPEN, JobStatus.DRAFT, JobStatus.CLOSED},
    JobStatus.OPEN: {JobStatus.PAUSED, JobStatus.CLOSED},
    JobStatus.PAUSED: {JobStatus.OPEN, JobStatus.CLOSED},
    JobStatus.CLOSED: {JobStatus.DRAFT},  # reopen as draft
}


def assert_job_transition(current: JobStatus, target: JobStatus) -> None:
    _assert_can_transition(JOB_TRANSITIONS, current, target, "job")


# ---------------------------------------------------------------------------
# Offer status
#   DRAFT -> PENDING_APPROVAL -> APPROVED -> SENT -> ACCEPTED | REJECTED
# ---------------------------------------------------------------------------

OFFER_TRANSITIONS: dict[OfferStatus, set[OfferStatus]] = {
    OfferStatus.DRAFT: {OfferStatus.PENDING_APPROVAL, OfferStatus.REJECTED},
    OfferStatus.PENDING_APPROVAL: {
        OfferStatus.APPROVED,
        OfferStatus.DRAFT,
        OfferStatus.REJECTED,
    },
    OfferStatus.APPROVED: {OfferStatus.SENT, OfferStatus.REJECTED},
    OfferStatus.SENT: {OfferStatus.ACCEPTED, OfferStatus.REJECTED},
    OfferStatus.ACCEPTED: set(),
    OfferStatus.REJECTED: set(),
}


def assert_offer_transition(current: OfferStatus, target: OfferStatus) -> None:
    _assert_can_transition(OFFER_TRANSITIONS, current, target, "offer")


# ---------------------------------------------------------------------------
# Interview status
#   SCHEDULED -> COMPLETED | CANCELLED | NO_SHOW
# ---------------------------------------------------------------------------

INTERVIEW_TRANSITIONS: dict[InterviewStatus, set[InterviewStatus]] = {
    InterviewStatus.SCHEDULED: {
        InterviewStatus.COMPLETED,
        InterviewStatus.CANCELLED,
        InterviewStatus.NO_SHOW,
    },
    InterviewStatus.COMPLETED: {InterviewStatus.REJECTED},
    InterviewStatus.CANCELLED: set(),
    InterviewStatus.NO_SHOW: set(),
    InterviewStatus.REJECTED: set(),
}


def assert_interview_transition(
    current: InterviewStatus, target: InterviewStatus
) -> None:
    _assert_can_transition(INTERVIEW_TRANSITIONS, current, target, "interview")
