"""Consent gate for tool execution risk classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .config import ConsentMode, RiskLevel

_RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}


@dataclass
class ConsentDecision:
    allowed: bool
    tool_name: str
    risk_level: RiskLevel
    reason: str


class ConsentGate:
    def __init__(self, mode: ConsentMode = ConsentMode.BLOCK_CRITICAL, tool_risk_levels: Optional[dict[str, RiskLevel]] = None, default_risk_level: RiskLevel = RiskLevel.MEDIUM) -> None:
        self._mode = mode
        self._tool_risk_levels = tool_risk_levels or {}
        self._default_risk_level = default_risk_level

    def classify(self, tool_name: str) -> RiskLevel:
        if tool_name in self._tool_risk_levels:
            return self._tool_risk_levels[tool_name]
        tool_lower = tool_name.lower()
        for known_tool, risk in self._tool_risk_levels.items():
            if known_tool.lower() in tool_lower or tool_lower in known_tool.lower():
                return risk
        return self._default_risk_level

    def check(self, tool_name: str) -> ConsentDecision:
        risk_level = self.classify(tool_name)
        if self._mode == ConsentMode.ALLOW_ALL:
            return ConsentDecision(allowed=True, tool_name=tool_name, risk_level=risk_level, reason="Consent mode: allow_all")
        if self._mode == ConsentMode.BLOCK_ALL:
            return ConsentDecision(allowed=False, tool_name=tool_name, risk_level=risk_level, reason=f"Consent mode: block_all (risk={risk_level.value})")
        if self._mode == ConsentMode.BLOCK_CRITICAL:
            threshold = RiskLevel.CRITICAL
        elif self._mode == ConsentMode.BLOCK_HIGH_AND_CRITICAL:
            threshold = RiskLevel.HIGH
        else:
            threshold = RiskLevel.CRITICAL
        if _RISK_ORDER[risk_level] >= _RISK_ORDER[threshold]:
            return ConsentDecision(allowed=False, tool_name=tool_name, risk_level=risk_level, reason=f"Risk level {risk_level.value} >= threshold {threshold.value}")
        return ConsentDecision(allowed=True, tool_name=tool_name, risk_level=risk_level, reason=f"Risk level {risk_level.value} below threshold {threshold.value}")

    def intercept(self, tool_name: str) -> ConsentDecision:
        return self.check(tool_name)
