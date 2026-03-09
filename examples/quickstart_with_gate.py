"""
LangChain + AIR Blackbox Gate — Quickstart Example

Shows how to connect a LangChain agent to the AIR Blackbox Gate
for centralized policy enforcement and audit trails.

Prerequisites:
    pip install air-langchain-trust langchain-openai

Run the Gate first:
    pip install air-blackbox[server]
    uvicorn gate.proxy:app --reload

Then run this script:
    python examples/quickstart_with_gate.py
"""

from air_langchain_trust import AirTrustCallbackHandler, AirTrustConfig

# ── Configure with Gate URL ──────────────────────────────────────
config = AirTrustConfig(
    gateway_url="http://localhost:8000",  # Gate server
    # gateway_key="your-api-key",        # Optional auth
)

handler = AirTrustCallbackHandler(config=config)

# ── Use with LangChain ──────────────────────────────────────────
# from langchain_openai import ChatOpenAI
# from langchain.agents import AgentExecutor, create_openai_tools_agent
#
# llm = ChatOpenAI(model="gpt-4")
# agent = AgentExecutor(agent=..., tools=[...])
# result = agent.invoke(
#     {"input": "Search for ML engineers in San Francisco"},
#     config={"callbacks": [handler]},
# )

# ── Standalone demo (no LangChain needed) ────────────────────────
print("AIR Blackbox LangChain Trust Layer v0.2.0")
print("=" * 50)

# Simulate what happens when a tool is called
from unittest.mock import MagicMock
from uuid import uuid4

run_id = uuid4()

# Simulate a search tool (should be auto-allowed by Gate)
print("\n1. Simulating search tool call...")
handler.on_tool_start(
    serialized={"name": "web_search"},
    input_str="ML engineers in San Francisco",
    run_id=run_id,
)
print("   -> Search tool: passed through")

# Simulate an email tool (should require approval via Gate)
print("\n2. Simulating email tool call...")
try:
    handler.on_tool_start(
        serialized={"name": "send_email"},
        input_str="Dear candidate, we have a role...",
        run_id=run_id,
    )
    print("   -> Email tool: passed through (auto-allowed or pending)")
except Exception as e:
    print(f"   -> Email tool: {e}")

# Check audit stats
print("\n3. Audit stats:")
stats = handler.get_audit_stats()
for k, v in stats.items():
    print(f"   {k}: {v}")

# Verify chain
print("\n4. Chain verification:")
chain = handler.verify_chain()
print(f"   Valid: {chain['valid']}")
print(f"   Entries: {chain['total_entries']}")

# Check if Gate is reachable
print("\n5. Gate connection:")
if handler.gate.is_configured:
    health = handler.gate.health_check()
    if health:
        print(f"   Connected to Gate: {health.get('status')}")
        print(f"   Gate events: {health.get('events_count')}")
    else:
        print("   Gate not reachable (running in local-only mode)")
else:
    print("   No Gate URL configured (local-only mode)")

print("\nDone! All tool calls logged with HMAC-SHA256 signatures.")
