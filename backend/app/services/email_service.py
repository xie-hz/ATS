"""Candidate-facing email notifications.

Synchronous + non-fatal: SMTP failures are logged but never break the business
operation (the stage change / offer send has already committed). When SMTP isn't
configured (`emails_enabled=False`) every function is a no-op, so the same code
path works in dev without a mail server.

For high volume these could be moved onto Celery tasks (`.delay()`); the
function signatures are kept simple to make that swap trivial later.
"""

from __future__ import annotations

import structlog
from sqlmodel import Session

from app.core.config import settings
from app.models import Application, ApplicationStage, Candidate, Job
from app.utils import send_email

logger = structlog.get_logger()

# Chinese labels for the candidate-facing stage name in status emails.
STAGE_LABELS: dict[str, str] = {
    "APPLIED": "已投递",
    "SCREENING": "简历筛选",
    "INTERVIEW": "面试中",
    "OFFER": "Offer 阶段",
    "HIRED": "已入职",
    "REJECTED": "未通过",
}


def _send(*, email_to: str, subject: str, html: str) -> None:
    """Send an email, swallowing failures so business ops stay unaffected."""
    if not settings.emails_enabled or not email_to:
        return
    try:
        response = send_email(email_to=email_to, subject=subject, html_content=html)
    except Exception as exc:  # noqa: BLE001 - any SMTP issue is non-fatal
        logger.warning("candidate_email_failed", to=email_to, error=str(exc))
        return
    # send_email returns None on the assert path; otherwise an SMTPResponse
    # whose `.success` is False (status_code != 250) means it didn't deliver.
    if not response or not response.success:
        logger.warning(
            "candidate_email_failed",
            to=email_to,
            error=repr(response.error) if response else "no response",
        )


def get_app_contact(
    *, session: Session, application_id
) -> tuple[str | None, str]:
    """Resolve (candidate email, job title) for an application."""
    app = session.get(Application, application_id)
    if not app:
        return None, ""
    cand = session.get(Candidate, app.candidate_id)
    job = session.get(Job, app.job_id)
    return (cand.email if cand else None), (job.title if job else "")


def send_application_submitted_email(
    *, email_to: str, job_title: str
) -> None:
    _send(
        email_to=email_to,
        subject=f"【{settings.PROJECT_NAME}】申请已提交",
        html=(
            f"<p>您好，</p>"
            f"<p>您对「{job_title}」职位的申请已成功提交，我们会尽快处理。</p>"
            f"<p>可登录候选人门户随时查看申请进度。</p>"
        ),
    )


def send_stage_changed_email(
    *,
    email_to: str,
    job_title: str,
    stage: ApplicationStage,
) -> None:
    label = STAGE_LABELS.get(stage.value, stage.value)
    if stage == ApplicationStage.REJECTED:
        body = (
            f"<p>您好，</p>"
            f"<p>很遗憾，您对「{job_title}」的申请本次未通过筛选。"
            f"感谢您的关注，祝您求职顺利。</p>"
        )
    elif stage == ApplicationStage.HIRED:
        body = (
            f"<p>您好，</p>"
            f"<p>恭喜您！您对「{job_title}」的申请已通过，欢迎加入我们。</p>"
        )
    else:
        body = (
            f"<p>您好，</p>"
            f"<p>您对「{job_title}」的申请状态已更新为：<strong>{label}</strong>。</p>"
        )
    _send(
        email_to=email_to,
        subject=f"【{settings.PROJECT_NAME}】申请状态更新",
        html=body,
    )


def send_interview_scheduled_email(
    *, email_to: str, job_title: str, scheduled_time, round: int
) -> None:
    when = scheduled_time.strftime("%Y-%m-%d %H:%M") if scheduled_time else "待定"
    _send(
        email_to=email_to,
        subject=f"【{settings.PROJECT_NAME}】面试邀请",
        html=(
            f"<p>您好，</p>"
            f"<p>您对「{job_title}」的申请已进入面试环节。</p>"
            f"<p>第 {round} 轮面试时间：<strong>{when}</strong></p>"
            f"<p>请准时参加，祝您面试顺利！</p>"
        ),
    )


def send_interview_cancelled_email(
    *, email_to: str, job_title: str, scheduled_time, round: int
) -> None:
    when = scheduled_time.strftime("%Y-%m-%d %H:%M") if scheduled_time else "原定时间"
    _send(
        email_to=email_to,
        subject=f"【{settings.PROJECT_NAME}】面试已取消",
        html=(
            f"<p>您好，</p>"
            f"<p>很抱歉，您对「{job_title}」第 {round} 轮面试"
            f"（原定 {when}）已取消。</p>"
            f"<p>如需重新安排，我们会另行通知，请留意邮箱。</p>"
        ),
    )


def send_offer_email(*, email_to: str, job_title: str, salary: int | None) -> None:
    salary_line = (
        f"<p>Offer 薪资：{salary}</p>" if salary else ""
    )
    _send(
        email_to=email_to,
        subject=f"【{settings.PROJECT_NAME}】Offer 通知",
        html=(
            f"<p>您好，</p>"
            f"<p>恭喜您通过「{job_title}」的招聘流程！您的 Offer 已发送。</p>"
            f"{salary_line}"
            f"<p>请登录候选人门户查看并确认。</p>"
        ),
    )
