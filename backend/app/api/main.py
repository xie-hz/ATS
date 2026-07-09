from fastapi import APIRouter

from app.api.routes.admin import (
    analytics as admin_analytics,
)
from app.api.routes.admin import (
    applications as admin_applications,
)
from app.api.routes.admin import (
    audit_logs as admin_audit_logs,
)
from app.api.routes.admin import (
    auth as admin_auth,
)
from app.api.routes.admin import (
    candidates as admin_candidates,
)
from app.api.routes.admin import (
    interviews as admin_interviews,
)
from app.api.routes.admin import (
    jobs as admin_jobs,
)
from app.api.routes.admin import (
    notifications as admin_notifications,
)
from app.api.routes.admin import (
    offers as admin_offers,
)
from app.api.routes.admin import (
    users as admin_users,
)
from app.api.routes.portal import (
    applications as portal_applications,
)
from app.api.routes.portal import (
    auth as portal_auth,
)
from app.api.routes.portal import (
    jobs as portal_jobs,
)
from app.api.routes.portal import (
    offers as portal_offers,
)

api_router = APIRouter()

# Internal (admin) API
api_router.include_router(admin_auth.router)
api_router.include_router(admin_users.router)
api_router.include_router(admin_jobs.router)
api_router.include_router(admin_candidates.router)
api_router.include_router(admin_applications.router)
api_router.include_router(admin_interviews.router)
api_router.include_router(admin_offers.router)
api_router.include_router(admin_notifications.router)
api_router.include_router(admin_audit_logs.router)
api_router.include_router(admin_analytics.router)

# Public (candidate) API
api_router.include_router(portal_jobs.router)
api_router.include_router(portal_auth.router)
api_router.include_router(portal_applications.router)
api_router.include_router(portal_offers.router)
