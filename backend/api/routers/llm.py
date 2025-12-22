from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.settings import settings
from core.llm.service import LlmService

router = APIRouter(prefix="/llm", tags=["llm"])

_llm = LlmService(llm_mode=settings.llm_mode)


class RewriteBulletsIn(BaseModel):
    bullets: list[str] = Field(default_factory=list)
    goal: str | None = None
    provider: str | None = Field(default="auto", description="auto|hosted|ollama")


class SuggestKeywordsIn(BaseModel):
    text: str
    provider: str | None = Field(default="auto", description="auto|hosted|ollama")


class ConsistencyCheckIn(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)
    provider: str | None = Field(default="auto", description="auto|hosted|ollama")


def _ensure_enabled() -> None:
    if not _llm.enabled():
        raise HTTPException(status_code=503, detail="LLM is disabled (set SEEWEE_LLM_MODE=hosted|ollama|both)")


@router.post("/rewrite_bullets")
def rewrite_bullets(payload: RewriteBulletsIn) -> dict:
    _ensure_enabled()
    r = _llm.rewrite_bullets(payload.bullets, goal=payload.goal, provider=payload.provider)
    return {"provider": r.provider, "note": r.note, "result": r.output}


@router.post("/suggest_keywords")
def suggest_keywords(payload: SuggestKeywordsIn) -> dict:
    _ensure_enabled()
    r = _llm.suggest_keywords(payload.text, provider=payload.provider)
    return {"provider": r.provider, "note": r.note, "result": r.output}


@router.post("/consistency_check")
def consistency_check(payload: ConsistencyCheckIn) -> dict:
    _ensure_enabled()
    r = _llm.consistency_check(payload.payload, provider=payload.provider)
    return {"provider": r.provider, "note": r.note, "result": r.output}


