"""Custom exceptions for the AIR Trust Layer."""

from __future__ import annotations

from typing import Any, Optional


class AirTrustError(Exception):
    """Base exception for all AIR Trust Layer errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.details = details or {}


class ConsentDeniedError(AirTrustError):
    """Raised when the consent gate blocks a tool call."""

    def __init__(self, tool_name: str, risk_level: str, reason: str) -> None:
        super().__init__(
            f"Consent denied for tool '{tool_name}': {reason}",
            details={"tool_name": tool_name, "risk_level": risk_level, "reason": reason},
        )
        self.tool_name = tool_name
        self.risk_level = risk_level


class InjectionBlockedError(AirTrustError):
    """Raised when a prompt injection is detected and blocked."""

    def __init__(self, pattern_name: str, matched_text: str) -> None:
        super().__init__(
            f"Injection detected (pattern: {pattern_name}): '{matched_text}'",
            details={"pattern_name": pattern_name, "matched_text": matched_text},
        )
        self.pattern_name = pattern_name
        self.matched_text = matched_text
