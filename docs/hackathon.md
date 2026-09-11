# NOVA Hackathon Strategy

## 1. Judging Strategy
To win, NOVA must stand out from reactive LLM wrappers by proving **Autonomy, Memory, and Proactivity**. 
We pitch the "mental load" of household management. NOVA is a proactive intelligence layer, not just a chatbot.
Technical impressiveness comes from the enterprise-grade stack (Strands SDK + AWS Serverless + Bedrock) and the strict separation of probabilistic LLM reasoning and deterministic rule enforcement.

## 2. MVP Priorities (The "Household Autopilot")
Focus on a single, relatable hero scenario: **The Sunday Evening Reset**.
Demonstrate:
- **Agentic Reasoning Loop:** Visible traces of the agent planning and acting.
- **Stateful Memory:** Remembering past preferences (DynamoDB + AgentCore).
- **Proactive Trigger:** EventBridge waking up the agent to perform actions.
- **Seamless AWS Integration.**

## 3. What to Mock
- **Physical IoT:** Mock smart home sensors and fridge inventories.
- **External Commerce:** Use a `MockCommerceAdapter` instead of real Instacart/Amazon APIs.
- **Auth:** Hardcode a single "Demo Household" profile to save time.

## 4. Risks & Mitigations
- **LLM Hallucinations:** Mitigated by strict system prompts and a deterministic boundary for math/spending.
- **Latency:** Use streaming responses and polished "NOVA is thinking..." UI states.
- **Live Demo Failure:** Pre-record a high-quality fallback video.

## 5. Demo Structure (3-Minute Pitch)
1. **0:00 - 0:45:** The Problem (Mental load) & Vision (NOVA: Intelligence layer).
2. **0:45 - 2:00:** The "Aha" Demo. Show proactive EventBridge trigger, autonomous inventory decision, and human-in-the-loop "Ask" fallback.
3. **2:00 - 2:40:** Under the Hood. Show the deterministic boundary and Strands SDK orchestration.
4. **2:40 - 3:00:** The Future. How this scales to everyday life.
