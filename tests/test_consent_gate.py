"""Tests for the consent gate."""

import pytest
from air_langchain_trust.config import ConsentMode, RiskLevel
from air_langchain_trust.consent_gate import ConsentGate


class TestConsentGate:
    def test_classify_known_tool(self):
        gate = ConsentGate(tool_risk_levels={"shell": RiskLevel.CRITICAL})
        assert gate.classify("shell") == RiskLevel.CRITICAL

    def test_classify_unknown_tool_uses_default(self):
        gate = ConsentGate(default_risk_level=RiskLevel.MEDIUM)
        assert gate.classify("unknown_tool") == RiskLevel.MEDIUM

    def test_classify_substring_match(self):
        gate = ConsentGate(tool_risk_levels={"shell": RiskLevel.CRITICAL})
        assert gate.classify("shell_exec") == RiskLevel.CRITICAL

    def test_block_critical_mode(self):
        gate = ConsentGate(mode=ConsentMode.BLOCK_CRITICAL, tool_risk_levels={"shell": RiskLevel.CRITICAL, "search": RiskLevel.LOW})
        assert gate.check("shell").allowed is False
        assert gate.check("search").allowed is True

    def test_block_high_and_critical_mode(self):
        gate = ConsentGate(mode=ConsentMode.BLOCK_HIGH_AND_CRITICAL, tool_risk_levels={"shell": RiskLevel.CRITICAL, "sql": RiskLevel.HIGH, "search": RiskLevel.LOW})
        assert gate.check("shell").allowed is False
        assert gate.check("sql").allowed is False
        assert gate.check("search").allowed is True

    def test_allow_all_mode(self):
        gate = ConsentGate(mode=ConsentMode.ALLOW_ALL, tool_risk_levels={"shell": RiskLevel.CRITICAL})
        assert gate.check("shell").allowed is True

    def test_block_all_mode(self):
        gate = ConsentGate(mode=ConsentMode.BLOCK_ALL, tool_risk_levels={"search": RiskLevel.LOW})
        assert gate.check("search").allowed is False

    def test_decision_includes_reason(self):
        gate = ConsentGate(mode=ConsentMode.BLOCK_CRITICAL, tool_risk_levels={"shell": RiskLevel.CRITICAL})
        decision = gate.check("shell")
        assert decision.reason
        assert decision.risk_level == RiskLevel.CRITICAL
