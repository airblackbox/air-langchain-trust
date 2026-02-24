"""PII tokenization vault."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


@dataclass
class TokenRecord:
    token: str
    original: str
    pattern_name: str


class DataVault:
    TOKEN_PREFIX = "[AIR_VAULT:"
    TOKEN_SUFFIX = "]"

    def __init__(self, patterns: Optional[dict[str, str]] = None) -> None:
        self._patterns: dict[str, re.Pattern] = {}
        self._vault: dict[str, TokenRecord] = {}
        default_patterns = {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "api_key": r"\b(?:sk|pk|api[_-]?key)[_-]?[A-Za-z0-9]{20,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        }
        raw_patterns = patterns if patterns is not None else default_patterns
        for name, pattern_str in raw_patterns.items():
            self._patterns[name] = re.compile(pattern_str, re.IGNORECASE)

    def tokenize(self, text: str) -> str:
        result = text
        for pattern_name, pattern in self._patterns.items():
            for match in pattern.finditer(result):
                original = match.group()
                if self.TOKEN_PREFIX in original:
                    continue
                token_id = uuid4().hex[:12]
                token = f"{self.TOKEN_PREFIX}{token_id}{self.TOKEN_SUFFIX}"
                record = TokenRecord(token=token, original=original, pattern_name=pattern_name)
                self._vault[token_id] = record
                result = result.replace(original, token, 1)
        return result

    def detokenize(self, text: str) -> str:
        result = text
        for token_id, record in self._vault.items():
            result = result.replace(record.token, record.original)
        return result

    def get_token_count(self) -> int:
        return len(self._vault)

    def get_token_records(self) -> list[TokenRecord]:
        return list(self._vault.values())

    def has_sensitive_data(self, text: str) -> bool:
        for pattern in self._patterns.values():
            if pattern.search(text):
                return True
        return False

    def clear(self) -> None:
        self._vault.clear()
