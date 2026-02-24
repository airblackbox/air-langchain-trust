"""AIR Trust Layer configuration."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConsentMode(str, Enum):
    ALLOW_ALL = "allow_all"
    BLOCK_CRITICAL = "block_critical"
    BLOCK_HIGH_AND_CRITICAL = "block_high_and_critical"
    BLOCK_ALL = "block_all"


class AirTrustConfig(BaseModel):
    """Configuration for the AIR Trust Layer."""

    enabled: bool = Field(default=True, description="Master switch for trust layer")
    audit_enabled: bool = Field(default=True)
    audit_secret: str = Field(default="air-trust-default-secret")
    vault_enabled: bool = Field(default=True)
    vault_patterns: dict[str, str] = Field(
        default_factory=lambda: {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "api_key": r"\b(?:sk|pk|api[_-]?key)[_-]?[A-Za-z0-9]{20,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        },
    )
    consent_enabled: bool = Field(default=True)
    consent_mode: ConsentMode = Field(default=ConsentMode.BLOCK_CRITICAL)
    tool_risk_levels: dict[str, RiskLevel] = Field(
        default_factory=lambda: {
            "shell": RiskLevel.CRITICAL,
            "bash": RiskLevel.CRITICAL,
            "exec": RiskLevel.CRITICAL,
            "delete": RiskLevel.CRITICAL,
            "rm": RiskLevel.CRITICAL,
            "sql": RiskLevel.HIGH,
            "database": RiskLevel.HIGH,
            "send_email": RiskLevel.HIGH,
            "http_request": RiskLevel.MEDIUM,
            "file_read": RiskLevel.LOW,
            "search": RiskLevel.LOW,
        },
    )
    default_risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    injection_enabled: bool = Field(default=True)
    injection_patterns: list[str] = Field(
        default_factory=lambda: [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"disregard\s+(all\s+)?prior\s+(instructions|context)",
            r"you\s+are\s+now\s+(?:a\s+)?(?:DAN|jailbreak|unrestricted)",
            r"system\s*:\s*you\s+(?:are|must|should|will)",
            r"<\|(?:system|im_start)\|>",
            r"ADMIN\s*OVERRIDE",
            r"BEGIN\s+(?:NEW\s+)?INSTRUCTIONS",
        ],
    )
    injection_block: bool = Field(default=True)
