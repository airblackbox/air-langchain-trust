# Adding EU AI Act Compliance to LangChain

**Package**: `air-langchain-trust` v0.2.0
**Last updated**: March 2026

---

## Before You Start

- Python 3.9+
- A LangChain project (any version ≥ 0.1)
- ~5 minutes to integrate
- Optional: AIR Blackbox Gate for centralized policy enforcement

## Step 1: Install

```bash
pip install air-langchain-trust
```

For Gate integration (optional):
```bash
pip install air-langchain-trust[gate]
```

## Step 2: Add the Trust Layer

The trust layer plugs in as a LangChain callback handler. Here's a minimal before/after:

**Before** (no compliance):
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")
result = llm.invoke("Summarize this contract")
```

**After** (EU AI Act compliant):
```python
from langchain_openai import ChatOpenAI
from air_langchain_trust import AirTrustCallbackHandler

handler = AirTrustCallbackHandler()
llm = ChatOpenAI(model="gpt-4o")
result = llm.invoke("Summarize this contract", config={"callbacks": [handler]})

# Every LLM call and tool execution is now logged in a tamper-evident audit chain
print(handler.get_audit_stats())
```

That's it. One import, one line of config. Your agent now produces cryptographically verifiable audit trails.

## Step 3: Verify It's Working

After running your agent, check the audit chain:

```python
stats = handler.get_audit_stats()
print(stats)
# {'total_events': 5, 'llm_calls': 2, 'tool_calls': 3, 'blocked': 0}

verification = handler.verify_chain()
print(verification)
# ChainVerification(valid=True, total_entries=5, verified_entries=5, errors=[])
```

If `valid=True`, your audit chain has cryptographic integrity — no entries have been tampered with or removed.

## Step 4: Run a Compliance Scan

Install the CLI scanner and scan your project:

```bash
pip install air-compliance
air-compliance scan .
```

Expected output with the trust layer active:
```
AIR Blackbox Compliance Scanner v1.x

Scanning: ./my_langchain_project

Article  9 — Risk Management:        PASS  (tool risk classification active)
Article 10 — Data Governance:         PASS  (PII detection enabled)
Article 11 — Technical Documentation: PASS  (audit chain exportable)
Article 12 — Record-Keeping:          PASS  (HMAC-SHA256 audit chain active)
Article 14 — Human Oversight:         PASS  (consent gate configured)
Article 15 — Robustness:              PASS  (injection detection enabled)

Result: 6/6 technical checks passing
```

## What's Happening Under the Hood

When you add `AirTrustCallbackHandler`, these features activate automatically:

1. **Audit Ledger** — Every LLM call and tool execution is logged with timestamps, inputs, outputs, and an HMAC-SHA256 hash linking each entry to the previous one. This creates a tamper-evident chain that satisfies Article 12 (Record-Keeping).

2. **Consent Gate** — Tools are classified by risk level (low/medium/high/critical). High-risk tools (file deletion, email sending, database writes) can be blocked or require approval. Satisfies Article 14 (Human Oversight).

3. **PII Detection** — Inputs are scanned for emails, phone numbers, SSNs, and other personally identifiable information. Detected PII is tokenized before logging. Supports Article 10 (Data Governance).

4. **Injection Detection** — Prompts are scanned for common injection patterns ("ignore previous instructions", encoded payloads). Suspicious inputs are flagged in the audit chain. Supports Article 15 (Robustness).

## Connecting to AIR Blackbox Gate (Optional)

Gate is a centralized policy server. Instead of each agent making its own allow/block decisions, Gate enforces organization-wide policies.

```python
from air_langchain_trust import AirTrustCallbackHandler, AirTrustConfig

config = AirTrustConfig(
    gateway_url="http://localhost:8000",  # Gate server URL
    # gateway_key="your-api-key",        # Optional API key
)

handler = AirTrustCallbackHandler(config=config)
```

With Gate connected:
- Tool calls are checked against Gate's policy before execution
- Gate can `auto_allow`, `require_approval`, or `block` based on centralized rules
- All decisions are logged in Gate's audit trail
- If Gate is unavailable, the trust layer falls back to local policy (graceful degradation)

See [Gate Setup Guide](../../air-gate/docs/setup-guide.md) for running the Gate server.

## Advanced Configuration

### Custom Tool Risk Levels

```python
from air_langchain_trust import AirTrustConfig, RiskLevel

config = AirTrustConfig(
    tool_risk_levels={
        "search_web": RiskLevel.LOW,
        "read_file": RiskLevel.MEDIUM,
        "send_email": RiskLevel.HIGH,
        "delete_database": RiskLevel.CRITICAL,
    }
)
handler = AirTrustCallbackHandler(config=config)
```

### Consent Gate Modes

```python
from air_langchain_trust import AirTrustConfig

# Block nothing (audit only)
config = AirTrustConfig(consent_mode="ALLOW_ALL")

# Block critical tools
config = AirTrustConfig(consent_mode="BLOCK_CRITICAL")

# Block high + critical tools
config = AirTrustConfig(consent_mode="BLOCK_HIGH_AND_CRITICAL")

# Block everything (require explicit allow-list)
config = AirTrustConfig(consent_mode="BLOCK_ALL")
```

### Export Audit Chain

```python
# Get the full audit chain as JSON (for regulatory submission)
chain_data = handler.export_chain()

# Save to file
import json
with open("audit_chain.json", "w") as f:
    json.dump(chain_data, f, indent=2)
```

## API Reference

### `AirTrustCallbackHandler`

The main entry point. Inherits from LangChain's `BaseCallbackHandler`.

| Method | Returns | Description |
|--------|---------|-------------|
| `get_audit_stats()` | `dict` | Event counts by type |
| `verify_chain()` | `ChainVerification` | Cryptographic integrity check |
| `export_chain()` | `list[dict]` | Full audit chain as JSON |
| `get_events()` | `list[AuditEntry]` | All audit entries |

### `GateClient`

HTTP client for AIR Blackbox Gate. Initialized automatically when `gateway_url` is set.

| Method | Returns | Description |
|--------|---------|-------------|
| `submit_action(...)` | `dict \| None` | Submit tool call for policy decision |
| `approve_action(event_id, ...)` | `dict \| None` | Approve a pending action |
| `reject_action(event_id, ...)` | `dict \| None` | Reject a pending action |
| `health_check()` | `dict \| None` | Check Gate server status |
| `verify_chain()` | `dict \| None` | Verify Gate's audit chain |

### `AirTrustConfig`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `consent_mode` | `str` | `"BLOCK_CRITICAL"` | Which risk levels to block |
| `tool_risk_levels` | `dict` | `{}` | Custom risk per tool name |
| `gateway_url` | `str \| None` | `None` | Gate server URL |
| `gateway_key` | `str \| None` | `None` | Gate API key |
| `hmac_key` | `str \| None` | auto-generated | Key for audit chain signing |

## FAQ

**Q: Does this send my code to the cloud?**
No. Everything runs locally. The audit chain is stored in memory by default. Gate is optional and self-hosted.

**Q: Does this slow down my agent?**
Negligible. The overhead is ~1ms per event (hashing + logging). PII detection adds ~5ms for typical inputs.

**Q: Is this legal compliance?**
No. AIR Blackbox checks *technical* requirements from the EU AI Act. It's a linter for AI governance — like ESLint for code style, but for compliance. Always consult legal counsel for actual compliance certification.

**Q: What if Gate is down?**
The trust layer falls back to local policy enforcement automatically. No downtime, no errors. Gate enhances but isn't required.

**Q: Can I use this with LangGraph?**
Yes. The callback handler works with both LangChain and LangGraph — pass it in the same `config={"callbacks": [handler]}` pattern.

---

*Document version: 1.0 — Applies to air-langchain-trust v0.2.0*
