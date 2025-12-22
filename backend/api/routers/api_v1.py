from __future__ import annotations

from fastapi import APIRouter

from api.routers.entries import router as entries_router
from api.routers.profile import router as profile_router
from api.routers.tags import router as tags_router
from api.routers.variants import router as variants_router

router = APIRouter(prefix="/api/v1")

router.include_router(entries_router)
router.include_router(variants_router)
router.include_router(tags_router)
router.include_router(profile_router)


