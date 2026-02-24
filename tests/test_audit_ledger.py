"""Tests for the HMAC-SHA256 audit ledger."""

import pytest
from air_langchain_trust.audit_ledger import AuditLedger


class TestAuditLedger:
    def test_append_creates_entry(self):
        ledger = AuditLedger()
        entry = ledger.append("tool_call", {"tool_name": "search"})
        assert entry.action == "tool_call"
        assert entry.details["tool_name"] == "search"
        assert entry.hmac_hash
        assert entry.entry_id

    def test_chain_links_entries(self):
        ledger = AuditLedger()
        e1 = ledger.append("action_1")
        e2 = ledger.append("action_2")
        assert e2.previous_hash == e1.hmac_hash

    def test_verify_chain_empty(self):
        assert AuditLedger().verify_chain() is True

    def test_verify_chain_valid(self):
        ledger = AuditLedger()
        ledger.append("a")
        ledger.append("b")
        ledger.append("c")
        assert ledger.verify_chain() is True

    def test_verify_chain_detects_tampering(self):
        ledger = AuditLedger()
        ledger.append("a")
        ledger.append("b")
        ledger._entries[0].details["tampered"] = True
        assert ledger.verify_chain() is False

    def test_get_entries_returns_copy(self):
        ledger = AuditLedger()
        ledger.append("a")
        entries = ledger.get_entries()
        entries.clear()
        assert len(ledger) == 1

    def test_get_entries_by_action(self):
        ledger = AuditLedger()
        ledger.append("tool_call")
        ledger.append("llm_call")
        ledger.append("tool_call")
        assert len(ledger.get_entries_by_action("tool_call")) == 2
        assert len(ledger.get_entries_by_action("llm_call")) == 1

    def test_different_secrets_produce_different_hashes(self):
        e1 = AuditLedger(secret="secret-a").append("test")
        e2 = AuditLedger(secret="secret-b").append("test")
        assert e1.hmac_hash != e2.hmac_hash

    def test_len(self):
        ledger = AuditLedger()
        assert len(ledger) == 0
        ledger.append("a")
        ledger.append("b")
        assert len(ledger) == 2

    def test_genesis_hash_used_for_first_entry(self):
        ledger = AuditLedger()
        entry = ledger.append("first")
        assert entry.previous_hash == ledger._genesis_hash
