from __future__ import annotations

from core.llm.providers.base import LlmProvider, LlmResult
from core.llm.providers.hosted_stub import HostedStubProvider
from core.llm.providers.ollama_stub import OllamaStubProvider


class LlmService:
    """
    Provider-agnostic LLM facade.

    MVP: stubbed providers so the API surface is in place without external deps.
    """

    def __init__(self, *, llm_mode: str):
        self._llm_mode = (llm_mode or "off").lower()
        self._hosted = HostedStubProvider()
        self._ollama = OllamaStubProvider()

    def _pick(self, preferred: str | None) -> LlmProvider:
        pref = (preferred or "auto").lower()
        if pref == "hosted":
            return self._hosted
        if pref == "ollama":
            return self._ollama
        # auto
        if self._llm_mode == "hosted":
            return self._hosted
        if self._llm_mode == "ollama":
            return self._ollama
        return self._hosted

    def enabled(self) -> bool:
        return self._llm_mode in {"hosted", "ollama", "both"}

    def rewrite_bullets(self, bullets: list[str], goal: str | None = None, provider: str | None = None) -> LlmResult:
        return self._pick(provider).rewrite_bullets(bullets, goal=goal)

    def suggest_keywords(self, text: str, provider: str | None = None) -> LlmResult:
        return self._pick(provider).suggest_keywords(text)

    def consistency_check(self, payload: dict, provider: str | None = None) -> LlmResult:
        return self._pick(provider).consistency_check(payload)



