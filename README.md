# air-langchain-trust

AIR Trust Layer plugin for LangChain. Adds audit logging, PII tokenization, consent gating, and prompt injection detection to any LangChain agent via a single callback handler.

Part of the [AIR Blackbox](https://github.com/airblackbox/gateway) ecosystem.

## Install

```bash
pip install air-langchain-trust
```

## Quick Start

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from air_langchain_trust import AirTrustCallbackHandler

handler = AirTrustCallbackHandler()

# Attach to any chain or agent
result = agent_executor.invoke(
    {"input": "What's the weather?"},
    config={"callbacks": [handler]},
)

# Inspect the audit trail
for entry in handler.audit.get_entries():
    print(f"{entry.action}: {entry.details}")
```

## What It Does

**AuditLedger** — HMAC-SHA256 chained log of every tool call, LLM invocation, and chain execution. Tamper-evident: if any entry is modified, the chain breaks.

**DataVault** — Tokenizes PII (emails, SSNs, credit cards, API keys) before it reaches your logs. Reversible for authorized use.

**ConsentGate** — Classifies tools by risk level (low/medium/high/critical) and blocks execution when risk exceeds your threshold. Raises `ConsentDeniedError`.

**InjectionDetector** — Scans prompts for injection patterns (instruction override, jailbreak, authority impersonation). Raises `InjectionBlockedError`.

## How Blocking Works

LangChain callbacks are observation-only — they can't return False to stop execution. This plugin raises custom exceptions (`ConsentDeniedError`, `InjectionBlockedError`) which halt the chain. Catch them in your application code:

```python
from air_langchain_trust.errors import ConsentDeniedError, InjectionBlockedError

try:
    result = agent.invoke(input, config={"callbacks": [handler]})
except ConsentDeniedError as e:
    print(f"Blocked: {e.tool_name} (risk: {e.risk_level})")
except InjectionBlockedError as e:
    print(f"Injection detected: {e.pattern_name}")
```

## Configuration

```python
from air_langchain_trust import AirTrustCallbackHandler, AirTrustConfig, ConsentMode, RiskLevel

config = AirTrustConfig(
    consent_mode=ConsentMode.BLOCK_HIGH_AND_CRITICAL,
    tool_risk_levels={
        "shell": RiskLevel.CRITICAL,
        "sql_query": RiskLevel.HIGH,
        "web_search": RiskLevel.LOW,
    },
    injection_block=True,
    vault_enabled=True,
    audit_secret="your-hmac-secret",
)

handler = AirTrustCallbackHandler(config=config)
```

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT
