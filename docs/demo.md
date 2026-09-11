# NOVA E2E Demo Scenarios

## Scenario 1: NOVA Takes Care of Milk (AUTO)
**Context:**
- Milk quantity is low (expected to run out tomorrow).
- Confidence is high.
- Usual product is available for ₹68.
- Auto-buy limit is ₹500. Category is allowed.

**Flow:**
1. EventBridge triggers NOVA's daily check.
2. NOVA evaluates inventory, sees milk is low.
3. Decision engine evaluates rules (Confidence>80, Price<500, Allowed Category).
4. Emits `AUTO` decision.
5. Executes purchase via mock commerce.
6. **User UI:** Sees "Milk was running low, so I took care of it." under "Recently taken care of."
7. **Explanation:** User clicks "Why?" and sees a plain-English explanation of the inventory, consumption rate, price, and budget check.

## Scenario 2: NOVA Does Nothing (DO_NOTHING)
**Context:**
- Cooking oil quantity is sufficient (expected remaining ~19 days).

**Flow:**
1. EventBridge triggers NOVA.
2. Evaluates cooking oil.
3. Decision engine sees sufficient stock.
4. Emits `DO_NOTHING`.
5. **User UI:** Sees "You have enough cooking oil for about 19 days, so I left it alone."
6. **Key Takeaway:** Demonstrates intelligence by knowing when *not* to act.

## Scenario 3: "I want to make Maggi tonight" (ASK / AUTO)
**Context:**
- User intent: "I want to make Maggi tonight."

**Flow:**
1. User types command in Home UI.
2. NOVA LLM understands intent and identifies requirements (Maggi noodles, water, maybe specific veggies based on memory).
3. Checks pantry. Finds missing items (e.g., Maggi is missing).
4. Checks preferred products, availability, and price.
5. Checks budget and rules.
6. Determines confidence.
7. **Decision:** 
   - If allowed: `AUTO` ("Take care of it").
   - If over budget or low confidence: `ASK` ("Needs your input").
8. **User UI:** The UI dynamically presents the plan. "Maggi is missing for tonight. [Review / Take care of it]".
