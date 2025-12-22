from __future__ import annotations

import re

from core.llm.providers.base import LlmProvider, LlmResult


class OllamaStubProvider(LlmProvider):
    name = "ollama_stub"

    def rewrite_bullets(self, bullets: list[str], goal: str | None = None) -> LlmResult:
        cleaned = [re.sub(r"\s+", " ", b).strip().rstrip(".") for b in bullets]
        return LlmResult(
            provider=self.name,
            output={"rewritten": cleaned, "goal": goal},
            note="Stub provider (no Ollama call). Enable real Ollama calls later.",
        )

    def suggest_keywords(self, text: str) -> LlmResult:
        words = re.findall(r"[A-Za-z][A-Za-z0-9+\-]{3,}", text)
        uniq: list[str] = []
        seen = set()
        for w in words:
            wl = w.lower()
            if wl in seen:
                continue
            seen.add(wl)
            uniq.append(w)
            if len(uniq) >= 15:
                break
        return LlmResult(provider=self.name, output={"keywords": uniq}, note="Stub keyword extraction.")

    def consistency_check(self, payload: dict) -> LlmResult:
        return LlmResult(provider=self.name, output={"issues": []}, note="Stub consistency checks.")


