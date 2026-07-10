"""Admin application management: list/get + stage transitions."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permissions
from app.models import (
    ApplicationCreate,
    ApplicationPublic,
    ApplicationsPublic,
    ApplicationStage,
    ApplicationTransition,
    BatchAdvance,
    BatchNotify,
    BatchNotifyResult,
    User,
)
from app.services import application_service

router = APIRouter(prefix="/admin/applications", tags=["admin-applications"])


@router.post("/batch-advance", response_model=ApplicationsPublic)
def batch_advance(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_ADVANCE))],
    body: BatchAdvance,
) -> Any:
    """Advance multiple applications to the same stage (best-effort)."""
    apps = application_service.batch_advance(
        session=session,
        user=current_user,
        application_ids=body.application_ids,
        target_stage=body.target_stage,
    )
    return ApplicationsPublic(
        data=[ApplicationPublic.model_validate(a) for a in apps],
        count=len(apps),
    )


@router.post(
    "/batch-notify",
    response_model=BatchNotifyResult,
    dependencies=[Depends(require_permission(Permissions.APPLICATION_ADVANCE))],
)
def batch_notify(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_ADVANCE))],
    body: BatchNotify,
) -> Any:
    """§16 batch notify: send an in-app message to each application's owner."""
    return application_service.batch_notify(
        session=session, user=current_user, notify_in=body
    )


@router.post("/", response_model=ApplicationPublic)
def create_application(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_ADVANCE))],
    body: ApplicationCreate,
) -> Any:
    """Manually create an application (candidate + job)."""
    app = application_service.create_application(
        session=session,
        user=current_user,
        candidate_id=body.candidate_id,
        job_id=body.job_id,
        source=body.source,
    )
    return ApplicationPublic.model_validate(app)


@router.get("/", response_model=ApplicationsPublic)
def list_applications(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_READ))],
    skip: int = 0,
    limit: int = 100,
    stage: ApplicationStage | None = None,
    job_id: uuid.UUID | None = None,
) -> Any:
    return application_service.list_applications(
        session=session,
        user=current_user,
        skip=skip,
        limit=limit,
        stage=stage,
        job_id=job_id,
    )


@router.get("/{application_id}", response_model=ApplicationPublic)
def get_application(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_READ))],
    application_id: uuid.UUID,
) -> Any:
    app = application_service.get_application(
        session=session, user=current_user, application_id=application_id
    )
    return ApplicationPublic.model_validate(app)


@router.post("/{application_id}/advance", response_model=ApplicationPublic)
def advance_application(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_ADVANCE))],
    application_id: uuid.UUID,
    body: ApplicationTransition,
) -> Any:
    app = application_service.advance_application(
        session=session,
        user=current_user,
        application_id=application_id,
        target_stage=body.target_stage,
    )
    return ApplicationPublic.model_validate(app)


@router.post("/{application_id}/reject", response_model=ApplicationPublic)
def reject_application(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_REJECT))],
    application_id: uuid.UUID,
) -> Any:
    app = application_service.reject_application(
        session=session, user=current_user, application_id=application_id
    )
    return ApplicationPublic.model_validate(app)


@router.post("/{application_id}/restore", response_model=ApplicationPublic)
def restore_application(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.APPLICATION_RESTORE))],
    application_id: uuid.UUID,
) -> Any:
    app = application_service.restore_application(
        session=session, user=current_user, application_id=application_id
    )
    return ApplicationPublic.model_validate(app)
