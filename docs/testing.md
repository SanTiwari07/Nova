# NOVA Testing Strategy

## 1. Inventory Tests
- **Stock Calculation:** Verify addition and subtraction of items.
- **Consumption (DCR):** Ensure moving average correctly predicts run-out dates.
- **Confidence:** Verify time-based decay of confidence scores.

## 2. Decision Tests
The deterministic engine must be rigorously tested against the following scenarios:
- Low stock + high confidence + allowed + under budget $\rightarrow$ `AUTO`
- Low confidence $\rightarrow$ `ASK`
- Over budget $\rightarrow$ `ASK`
- Restricted category $\rightarrow$ `BLOCKED`
- Enough inventory $\rightarrow$ `DO_NOTHING`
- Commerce unavailable $\rightarrow$ `WAIT`

## 3. Commerce Tests
- Test the `CommerceInterface` independently of any provider.
- Use `mock_adapter.py` to simulate network latency, out-of-stock items, and successful checkouts.

## 4. Agent Tests
- Verify tool invocation parsing (e.g., that the LLM correctly extracts intent and calls `check_pantry`).
- Test end-to-end flows with mocked LLM responses.

## 5. E2E Demo Tests
- Automate tests for all three primary demo scenarios to ensure hackathon stability.
