"""Tests for the PII tokenization vault."""

import pytest
from air_langchain_trust.data_vault import DataVault


class TestDataVault:
    def test_tokenize_email(self):
        vault = DataVault()
        result = vault.tokenize("Contact bob@example.com for details")
        assert "bob@example.com" not in result
        assert "[AIR_VAULT:" in result

    def test_tokenize_ssn(self):
        vault = DataVault()
        result = vault.tokenize("SSN: 123-45-6789")
        assert "123-45-6789" not in result
        assert "[AIR_VAULT:" in result

    def test_tokenize_credit_card(self):
        vault = DataVault()
        result = vault.tokenize("Card: 4111-1111-1111-1111")
        assert "4111-1111-1111-1111" not in result

    def test_detokenize_restores_original(self):
        vault = DataVault()
        original = "Email: bob@example.com"
        tokenized = vault.tokenize(original)
        restored = vault.detokenize(tokenized)
        assert restored == original

    def test_has_sensitive_data_true(self):
        assert DataVault().has_sensitive_data("SSN is 123-45-6789") is True

    def test_has_sensitive_data_false(self):
        assert DataVault().has_sensitive_data("nothing sensitive here") is False

    def test_token_count(self):
        vault = DataVault()
        vault.tokenize("bob@example.com and 123-45-6789")
        assert vault.get_token_count() == 2

    def test_clear(self):
        vault = DataVault()
        vault.tokenize("bob@example.com")
        vault.clear()
        assert vault.get_token_count() == 0

    def test_no_double_tokenize(self):
        vault = DataVault()
        t1 = vault.tokenize("bob@example.com")
        t2 = vault.tokenize(t1)
        assert t1 == t2
