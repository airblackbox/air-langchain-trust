"""Prompt injection detection."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class InjectionResult:
    detected: bool
    pattern_name: str | None = None
    matched_text: str | None = None


class InjectionDetector:
    def __init__(self, patterns: list[str] | None = None) -> None:
        default_patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"disregard\s+(all\s+)?prior\s+(instructions|context)",
            r"you\s+are\s+now\s+(?:a\s+)?(?:DAN|jailbreak|unrestricted)",
            r"system\s*:\s*you\s+(?:are|must|should|will)",
            r"<\|(?:system|im_start)\|>",
            r"ADMIN\s*OVERRIDE",
            r"BEGIN\s+(?:NEW\s+)?INSTRUCTIONS",
        ]
        raw_patterns = patterns if patterns is not None else default_patterns
        self._patterns: list[tuple[str, re.Pattern]] = []
        for i, p in enumerate(raw_patterns):
            self._patterns.append((f"pattern_{i}", re.compile(p, re.IGNORECASE)))

    def scan(self, text: str) -> InjectionResult:
        for name, pattern in self._patterns:
            match = pattern.search(text)
            if match:
                return InjectionResult(detected=True, pattern_name=name, matched_text=match.group())
        return InjectionResult(detected=False)

    def scan_multiple(self, texts: list[str]) -> InjectionResult:
        for text in texts:
            result = self.scan(text)
            if result.detected:
                return result
        return InjectionResult(detected=False)
