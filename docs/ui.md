# NOVA UI Design System

## 1. Visual Identity
**Philosophy:** Premium SaaS × Intelligent Everyday Assistant
**Influence:** JungleMind (elegant AI interaction), Premium SaaS (Linear, Notion, Arc).
**Vibe:** Calm, intelligent, trustworthy, warm, effortless. No aggressive "AI" branding.

## 2. Color Palette
- **Background:** Warm off-white (`#FCFBF9`)
- **Surfaces:** Pure White (`#FFFFFF`)
- **Primary Text:** Deep charcoal (`#1C1C1C` to `#2D2D2D`)
- **Secondary Text:** Muted grey (`#6B7280`)
- **Action/Commerce:** Amazon orange/yellow (`#FF9900` - used sparingly)
- **Semantic:** Blue (links), Green (success), Warm red/brown (warning/blocking)

## 3. Typography
- **Primary Font:** Inter or Geist (clean, premium sans-serif).
- **Hierarchy:** Large legible typography, generous whitespace.

## 4. Navigation
Clean and abstracted. No dense enterprise toolbars.
- **Home**: The "Today" view. Central command and briefing.
- **Pantry**: Visual inventory. Focus on what's running low.
- **Plans**: Forward-looking view (meals, routines).
- **Orders**: Logistics hub.
- **Budget**: Financial summaries.
- **Rules**: Automation engine settings.

## 5. System State Translations
Technical states must be translated into natural language:
- `AUTO` $\rightarrow$ "Taken care of" / "Done for you"
- `ASK` $\rightarrow$ "Needs your input" / "Waiting for your okay"
- `WAIT` $\rightarrow$ "Waiting"
- `DO_NOTHING` $\rightarrow$ "No action needed" / "All sorted"
- `BLOCKED` $\rightarrow$ "Can't do this under your rules" / "Needs your attention"

## 6. The Explanation Experience ("Why?")
Every autonomous action has a "Why?" button.
NOVA explains in plain English: "Milk was running low. You usually finish this amount in about 5 days... Your automatic purchase limit is ₹500. So NOVA took care of it."
Do NOT expose raw logs, JSON, or complex rule IDs.
