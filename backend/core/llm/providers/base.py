from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmResult:
    provider: str
    output: object
    note: str = ""


class LlmProvider:
    name: str

    def rewrite_bullets(self, bullets: list[str], goal: str | None = None) -> LlmResult:
        raise NotImplementedError

    def suggest_keywords(self, text: str) -> LlmResult:
        raise NotImplementedError

    def consistency_check(self, payload: dict) -> LlmResult:
        raise NotImplementedError



