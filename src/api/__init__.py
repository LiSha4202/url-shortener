from fastapi import APIRouter

from .v1.routes.auth import router as auth_router
from .v1.routes.links import router as link_router
from .v1.routes.redirects import router as redirect_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(redirect_router)
router.include_router(link_router)
