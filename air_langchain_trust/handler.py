"""LangChain callback handler for the AIR Trust Layer."""

from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from .audit_ledger import AuditLedger
from .config import AirTrustConfig
from .consent_gate import ConsentGate
from .data_vault import DataVault
from .errors import ConsentDeniedError, InjectionBlockedError
from .injection_detector import InjectionDetector

logger = logging.getLogger(__name__)


class AirTrustCallbackHandler(BaseCallbackHandler):
    def __init__(self, config: Optional[AirTrustConfig] = None) -> None:
        super().__init__()
        self.config = config or AirTrustConfig()
        self.audit = AuditLedger(secret=self.config.audit_secret)
        self.vault = DataVault(patterns=self.config.vault_patterns if self.config.vault_enabled else {})
        self.consent = ConsentGate(mode=self.config.consent_mode, tool_risk_levels=self.config.tool_risk_levels, default_risk_level=self.config.default_risk_level)
        self.injection = InjectionDetector(patterns=self.config.injection_patterns)

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, *, run_id: UUID, parent_run_id: Optional[UUID] = None, tags: Optional[list[str]] = None, metadata: Optional[dict[str, Any]] = None, inputs: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        if not self.config.enabled:
            return
        tool_name = serialized.get("name", "unknown_tool")
        if self.config.consent_enabled:
            decision = self.consent.intercept(tool_name)
            if not decision.allowed:
                self.audit.append(action="consent_denied", details={"tool_name": tool_name, "risk_level": decision.risk_level.value, "reason": decision.reason, "run_id": str(run_id)})
                raise ConsentDeniedError(tool_name=tool_name, risk_level=decision.risk_level.value, reason=decision.reason)
        safe_input = input_str
        if self.config.vault_enabled:
            safe_input = self.vault.tokenize(input_str)
        if self.config.audit_enabled:
            self.audit.append(action="tool_call", details={"tool_name": tool_name, "input": safe_input, "run_id": str(run_id)})

    def on_tool_end(self, output: Any, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        if not self.config.enabled or not self.config.audit_enabled:
            return
        safe_output = str(output)
        if self.config.vault_enabled:
            safe_output = self.vault.tokenize(safe_output)
        self.audit.append(action="tool_result", details={"output": safe_output[:500], "run_id": str(run_id)})

    def on_tool_error(self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        if not self.config.enabled or not self.config.audit_enabled:
            return
        self.audit.append(action="tool_error", details={"error": str(error)[:500], "error_type": type(error).__name__, "run_id": str(run_id)})

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], *, run_id: UUID, parent_run_id: Optional[UUID] = None, tags: Optional[list[str]] = None, metadata: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        if not self.config.enabled:
            return
        if self.config.injection_enabled:
            result = self.injection.scan_multiple(prompts)
            if result.detected:
                self.audit.append(action="injection_blocked", details={"pattern_name": result.pattern_name, "matched_text": result.matched_text, "run_id": str(run_id)})
                if self.config.injection_block:
                    raise InjectionBlockedError(pattern_name=result.pattern_name or "unknown", matched_text=result.matched_text or "")
        safe_prompts = prompts
        if self.config.vault_enabled:
            safe_prompts = [self.vault.tokenize(p) for p in prompts]
        if self.config.audit_enabled:
            model_name = serialized.get("kwargs", {}).get("model_name", "unknown")
            self.audit.append(action="llm_call", details={"model": model_name, "prompt_count": len(prompts), "prompts": [p[:200] for p in safe_prompts], "run_id": str(run_id)})

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        if not self.config.enabled or not self.config.audit_enabled:
            return
        output_texts = []
        for gen_list in response.generations:
            for gen in gen_list:
                output_texts.append(gen.text[:200])
        self.audit.append(action="llm_output", details={"outputs": output_texts, "run_id": str(run_id)})

    def on_llm_error(self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        if not self.config.enabled or not self.config.audit_enabled:
            return
        self.audit.append(action="llm_error", details={"error": str(error)[:500], "error_type": type(error).__name__, "run_id": str(run_id)})

    def on_chain_start(self, serialized: dict[str, Any], inputs: dict[str, Any], *, run_id: UUID, parent_run_id: Optional[UUID] = None, tags: Optional[list[str]] = None, metadata: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        if not self.config.enabled or not self.config.audit_enabled:
            return
        chain_name = serialized.get("name", serialized.get("id", ["unknown"])[-1])
        self.audit.append(action="chain_start", details={"chain_name": str(chain_name), "input_keys": list(inputs.keys()) if isinstance(inputs, dict) else [], "run_id": str(run_id)})

    def on_chain_end(self, outputs: dict[str, Any], *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        if not self.config.enabled or not self.config.audit_enabled:
            return
        self.audit.append(action="chain_end", details={"output_keys": list(outputs.keys()) if isinstance(outputs, dict) else [], "run_id": str(run_id)})

    def on_chain_error(self, error: BaseException, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        if not self.config.enabled or not self.config.audit_enabled:
            return
        self.audit.append(action="chain_error", details={"error": str(error)[:500], "error_type": type(error).__name__, "run_id": str(run_id)})
