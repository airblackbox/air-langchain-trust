"""HMAC-SHA256 tamper-evident audit ledger."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4


@dataclass
class AuditEntry:
    """A single entry in the audit ledger."""
    entry_id: str
    timestamp: float
    action: str
    details: dict[str, Any]
    hmac_hash: str
    previous_hash: str


class AuditLedger:
    """HMAC-SHA256 chained audit ledger."""

    def __init__(self, secret: str = "air-trust-default-secret") -> None:
        self._secret = secret.encode("utf-8")
        self._entries: list[AuditEntry] = []
        self._genesis_hash = self._compute_hmac("genesis")

    def append(self, action: str, details: Optional[dict[str, Any]] = None) -> AuditEntry:
        details = details or {}
        entry_id = str(uuid4())
        timestamp = time.time()
        previous_hash = self._entries[-1].hmac_hash if self._entries else self._genesis_hash
        payload = json.dumps({"entry_id": entry_id, "timestamp": timestamp, "action": action, "details": details, "previous_hash": previous_hash}, sort_keys=True, default=str)
        hmac_hash = self._compute_hmac(payload)
        entry = AuditEntry(entry_id=entry_id, timestamp=timestamp, action=action, details=details, hmac_hash=hmac_hash, previous_hash=previous_hash)
        self._entries.append(entry)
        return entry

    def verify_chain(self) -> bool:
        if not self._entries:
            return True
        if self._entries[0].previous_hash != self._genesis_hash:
            return False
        for i, entry in enumerate(self._entries):
            previous_hash = self._entries[i - 1].hmac_hash if i > 0 else self._genesis_hash
            payload = json.dumps({"entry_id": entry.entry_id, "timestamp": entry.timestamp, "action": entry.action, "details": entry.details, "previous_hash": previous_hash}, sort_keys=True, default=str)
            expected_hash = self._compute_hmac(payload)
            if entry.hmac_hash != expected_hash:
                return False
        return True

    def get_entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def get_entries_by_action(self, action: str) -> list[AuditEntry]:
        return [e for e in self._entries if e.action == action]

    def __len__(self) -> int:
        return len(self._entries)

    def _compute_hmac(self, data: str) -> str:
        return hmac.new(self._secret, data.encode("utf-8"), hashlib.sha256).hexdigest()
