# NOVA Risks & Mitigations

## 1. LLM Hallucinations
**Risk:** The LLM might hallucinate inventory, prices, or attempt to overspend.
**Mitigation:** Strict separation of concerns. The LLM handles natural language and intent; a deterministic layer handles math, policy enforcement, and commerce. The LLM never holds API keys for payments.

## 2. Live Demo Latency
**Risk:** LLM API calls and multiple tool execution roundtrips can cause awkward silences during a hackathon demo.
**Mitigation:** Use streaming responses where possible. Design the UI to show "NOVA is thinking..." and provide visual traces of the agent's reasoning process.

## 3. High Variance Consumption
**Risk:** Predicting consumption of high-variance items (like snacks) is notoriously difficult and leads to false positives (buying too much or too little).
**Mitigation:** Rapid confidence decay for high-variance items, naturally forcing the system into an `ASK` state so the user remains in control.

## 4. Feature Creep
**Risk:** Attempting to build real integrations (Swiggy, Amazon Fresh, Smart Fridges) during the hackathon.
**Mitigation:** Strictly adhere to the MVP definition. Use `mock_adapter.py` for commerce and seed data for inventory.

## 5. Live Infrastructure Failure
**Risk:** AWS EventBridge, Bedrock, or DynamoDB issues during the pitch.
**Mitigation:** Always pre-record a high-quality fallback video of the working end-to-end demo.
