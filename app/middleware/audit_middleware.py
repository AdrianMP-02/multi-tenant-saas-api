from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.database import session_factory
from app.models.audit_log import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        if request.method in ("POST", "PUT", "PATCH", "DELETE") and response.status_code < 400:
            tc = getattr(request.state, "tenant_context", None)
            if tc:
                async with session_factory() as session:
                    log = AuditLog(
                        tenant_id=getattr(tc, "tenant_id", None),
                        user_id=getattr(request.state, "user_id", None),
                        action=f"{request.method}_{request.url.path}",
                        resource=request.url.path,
                        details={"status_code": response.status_code},
                        ip_address=request.client.host if request.client else None,
                    )
                    session.add(log)
                    await session.commit()

        return response
