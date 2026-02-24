"""AIR Trust Layer for LangChain.

Provides audit logging, PII tokenization, consent gating, and
injection detection for LangChain agents via a callback handler.

Usage::

    from air_langchain_trust import AirTrustCallbackHandler

    handler = AirTrustCallbackHandler()
    chain.invoke(input, config={"callbacks": [handler]})
"""

from .audit_ledger import AuditEntry, AuditLedger
from .config import AirTrustConfig, ConsentMode, RiskLevel
from .consent_gate import ConsentDecision, ConsentGate
from .data_vault import DataVault, TokenRecord
from .errors import AirTrustError, ConsentDeniedError, InjectionBlockedError
from .handler import AirTrustCallbackHandler
from .injection_detector import InjectionDetector, InjectionResult

__version__ = "0.1.0"

__all__ = [
    "AirTrustCallbackHandler",
    "AirTrustConfig",
    "ConsentMode",
    "RiskLevel",
    "AuditLedger",
    "AuditEntry",
    "DataVault",
    "TokenRecord",
    "ConsentGate",
    "ConsentDecision",
    "InjectionDetector",
    "InjectionResult",
    "AirTrustError",
    "ConsentDeniedError",
    "InjectionBlockedError",
]
