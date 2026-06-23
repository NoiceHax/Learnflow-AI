"""LLM call-site registry: who calls the API, when, and expected cost.

All runtime paths should be listed here. Update when adding new LLM usage.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmCallSite:
    caller: str
    trigger: str
    frequency: str
    cost_note: str
    page_load: bool
    requires_ai: bool


# fmt: off
LLM_CALL_SITES: tuple[LlmCallSite, ...] = (
    LlmCallSite(
        caller="probe_llm",
        trigger="Startup / GET /api/health?refresh=true",
        frequency="Once per process (cached 90s on failure); optional health refresh",
        cost_note="~1 token ping; max_tokens=8",
        page_load=False,
        requires_ai=False,
    ),
    LlmCallSite(
        caller="ask_socrates",
        trigger="POST /api/socrates/chat (user sends a message)",
        frequency="Per user message only; never on page load",
        cost_note="~600 output tokens; cached by message+context hash",
        page_load=False,
        requires_ai=False,
    ),
    LlmCallSite(
        caller="generate_questions → remediation",
        trigger="POST /api/quiz/{id}/submit after wrong answers (replenish_pool)",
        frequency="Only after quiz submit with retired questions; not on quiz load",
        cost_note="Up to 4096 tokens JSON; DB cache checked first",
        page_load=False,
        requires_ai=False,
    ),
)
# fmt: on


def audit_summary() -> list[dict[str, str]]:
    return [
        {
            "caller": s.caller,
            "trigger": s.trigger,
            "frequency": s.frequency,
            "cost_note": s.cost_note,
            "page_load": str(s.page_load),
            "required_for_basic_app": str(s.requires_ai),
        }
        for s in LLM_CALL_SITES
    ]
