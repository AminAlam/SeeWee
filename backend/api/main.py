from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.api_v1 import router as api_v1_router
from api.routers.health import router as health_router
from api.routers.llm import router as llm_router
from api.settings import settings
from core.migrations import upgrade_to_head


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        upgrade_to_head()
        yield

    app = FastAPI(title="SeeWee API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(api_v1_router)
    app.include_router(llm_router)
    return app


app = create_app()


