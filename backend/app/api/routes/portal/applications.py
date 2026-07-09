"""Portal applications: submit (public) + list/get own (portal token)."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_portal_email
from app.models import Job, PortalApplicationPublic, PortalApplicationSubmit
from app.services import portal_service

router = APIRouter(prefix="/portal/applications", tags=["portal-applications"])


@router.post("/", response_model=PortalApplicationPublic)
def submit_application(
    session: SessionDep, submit_in: PortalApplicationSubmit
) -> Any:
    app = portal_service.submit_application(session=session, submit_in=submit_in)
    job = session.get(Job, app.job_id)
    return PortalApplicationPublic(
        id=app.id,
        job_id=app.job_id,
        job_title=job.title if job else "",
        stage=app.stage,
        created_at=app.created_at,
    )


@router.get("/", response_model=list[PortalApplicationPublic])
def list_my_applications(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
) -> Any:
    return portal_service.list_portal_applications(session=session, email=email)


@router.get("/{application_id}", response_model=PortalApplicationPublic)
def get_my_application(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
    application_id: uuid.UUID,
) -> Any:
    return portal_service.get_portal_application(
        session=session, application_id=application_id, email=email
    )
