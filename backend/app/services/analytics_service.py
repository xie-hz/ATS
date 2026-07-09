"""Analytics service: hiring funnel, counts, channel effectiveness."""

from sqlmodel import Session, func, select

from app.models import Application, ApplicationStage, Candidate, Job, JobStatus


def get_summary(*, session: Session) -> dict:
    total_jobs = session.exec(select(func.count()).select_from(Job)).one()
    open_jobs = session.exec(
        select(func.count()).select_from(Job).where(Job.status == JobStatus.OPEN)
    ).one()
    total_candidates = session.exec(
        select(func.count()).select_from(Candidate)
    ).one()
    total_applications = session.exec(
        select(func.count()).select_from(Application)
    ).one()

    funnel: dict[str, int] = {}
    for stage in ApplicationStage:
        funnel[stage.value] = session.exec(
            select(func.count())
            .select_from(Application)
            .where(Application.stage == stage)
        ).one()

    rows = session.exec(
        select(Application.source, func.count())
        .select_from(Application)
        .group_by(Application.source)
    ).all()
    channels = {(src or "unknown"): cnt for src, cnt in rows}

    hired = funnel.get("HIRED", 0)
    conversion_rate = (
        round(hired / total_applications * 100, 1) if total_applications else 0
    )

    return {
        "total_jobs": total_jobs,
        "open_jobs": open_jobs,
        "total_candidates": total_candidates,
        "total_applications": total_applications,
        "funnel": funnel,
        "channels": channels,
        "hired": hired,
        "conversion_rate": conversion_rate,
    }
