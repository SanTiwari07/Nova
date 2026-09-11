# NOVA Data Models

## 9. Household State Model
- **Members:** Profiles of users in the household.
- **Preferences:** Global household preferences (e.g., dietary restrictions).
- **Routines:** Scheduled recurring needs (e.g., "Sunday Reset", "Taco Tuesday").
- **Active Intents:** Current goals or shopping trips in progress.

## 10. Inventory Model
- **Pantry State:** The current ledger of all items.
- **Item/Variant:** Normalized item (Milk) vs Specific SKU (Horizon Organic).
- **Quantity & Status:** Numeric stock level and last verified timestamp.
- **Consumption (DCR):** Moving average daily consumption rate.
- **Forecast:** Estimated current quantity based on DCR and time elapsed.
- **Confidence:** Score (0-100%) that decays over time if not verified.

## 11. Intent Model
- **Natural Language:** The raw string (e.g., "I want to make Maggi tonight").
- **Parsed Intent:** Structured goal (e.g., `Action=COOK`, `Target=Maggi`).
- **Requirements:** Derived needed items (Maggi noodles, Vegetables).

## 12. Decision Model
- **Evaluation Matrix:** Inputs (Inventory, Confidence, Budget, Policy) $\rightarrow$ Output State.
- **States:** `AUTO`, `ASK`, `WAIT`, `DO_NOTHING`, `BLOCKED`.
- **Reasoning:** Human-readable explanation of why the state was chosen.

## 13. Budget Model
- **Limits:** Monthly, weekly, or category-specific spending caps.
- **Auto-Spend Threshold:** Maximum amount NOVA can spend without asking (e.g., ₹500).
- **Current Spend:** Ledger of authorized purchases for the period.

## 14. Policy Model
- **Rules:** User-defined autonomy constraints.
- **Category Restrictions:** Allowed/Denied lists.
- **Overrides:** Specific brand pinning ("Always buy Brand X").

## 15. Authorization Model
- **Context Auth:** Link between the action and the verified household.
- **Approval Tokens:** Records of user explicit "OK" for `ASK` states.
