from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.core.permissions import (
    ALL_PERMISSIONS,
    ROLE_DATA_SCOPE,
    ROLE_PERMISSIONS,
    Roles,
)
from app.models import (
    DataScope,
    Department,
    Permission,
    Role,
    RolePermission,
    UserCreate,
)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """Idempotently seed permissions, roles, data scopes, a default
    department, and the first admin user.
    """
    # 1. Permissions
    for code in ALL_PERMISSIONS:
        if not crud.get_permission_by_code(session=session, code=code):
            session.add(Permission(code=code, description=code))
    session.commit()

    # 2. Roles + data scopes + role-permission links
    for role_code, perm_codes in ROLE_PERMISSIONS.items():
        role = crud.get_role_by_code(session=session, code=role_code)
        if not role:
            role = Role(
                name=role_code.replace("_", " ").title(),
                code=role_code,
            )
            session.add(role)
            session.commit()
            session.refresh(role)

        existing_scope = session.exec(
            select(DataScope).where(DataScope.role_id == role.id)
        ).first()
        if not existing_scope:
            session.add(
                DataScope(
                    role_id=role.id,
                    scope_type=ROLE_DATA_SCOPE[role_code],
                )
            )
            session.commit()

        for code in perm_codes:
            perm = crud.get_permission_by_code(session=session, code=code)
            if not perm:
                continue
            link = session.exec(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            ).first()
            if not link:
                session.add(
                    RolePermission(role_id=role.id, permission_id=perm.id)
                )
        session.commit()

    # 3. Default department
    dept = session.exec(select(Department)).first()
    if not dept:
        dept = Department(name="Engineering")
        session.add(dept)
        session.commit()
        session.refresh(dept)

    # 4. First admin user
    user = crud.get_user_by_email(session=session, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            name="Admin",
            department_id=dept.id,
            role_codes=[Roles.ADMIN],
        )
        user = crud.create_user(session=session, user_create=user_in)
        admin_role = crud.get_role_by_code(session=session, code=Roles.ADMIN)
        if admin_role:
            crud.assign_role(session=session, user=user, role=admin_role)
            session.commit()
