from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.billing import router as billing_router
from app.api.v1.feature_flags import router as feature_flags_router
from app.api.v1.plans import router as plans_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.users import router as users_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(tenants_router)
router.include_router(users_router)
router.include_router(plans_router)
router.include_router(feature_flags_router)
router.include_router(billing_router)
