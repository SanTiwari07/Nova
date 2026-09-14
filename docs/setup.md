# NOVA Local Development and Quickstart Guide

## 1. Zero-Cost-First Strategy
Development prioritizes local environments, simulated commerce, seeded household state, and controlled cloud usage. NOVA can run entirely locally without requiring active AWS or external commerce credentials.

## 2. Environment Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (tested on Node.js 20+)
- npm or pnpm

### Backend (Python / FastAPI)
1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Copy `.env.example` to `.env` in the repository root or `backend/`:
   ```bash
   cp ../.env.example ../.env
   ```
   Key variables:
   - `LLM_PROVIDER`: `gemini` (default for quick testing), `bedrock` (Amazon Bedrock Claude 3.5 Sonnet), or offline deterministic fallback.
   - `COMMERCE_MODE`: `live` (Swiggy Instamart MCP via JSON-RPC 2.0) or `mock` (deterministic local catalog).
   - `DEFAULT_AUTONOMY_PROFILE`: `FULL_AUTOPILOT`, `ASK_EVERYTHING`, or `RESTRICTIVE`.
5. Start the FastAPI backend server:
   ```bash
   python -m uvicorn api.main:app --reload --port 8000
   ```
   The interactive OpenAPI docs are accessible at `http://localhost:8000/docs`.

### Frontend (Next.js 14)
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Or create a production build:
   ```bash
   npm run build
   npm start
   ```
   Open `http://localhost:3000` to access the NOVA Command Center.

## 3. Seed Data & State Persistence
- Seed data is loaded automatically from `backend/inventory/inventory_service.py` (`DEMO_PANTRY`), initializing realistic Indian grocery staples (Amul Milk, Fortune Sunflower Oil, Aashirvaad Atta, Tata Salt, etc.).
- State changes (pantry levels, budget spend, audit trail) are persisted to `backend/data/*_state.json`.
- To reset the demo state at any time, click "Reset Demo State" in the UI header or call `POST /api/demo/reset`.

## 4. Running the Test Suite
The backend includes a comprehensive 32-test automated verification suite covering all hero scenarios, deterministic guardrails, cooking intent reconciliation, and edge cases:
```bash
# From repository root
python -m pytest backend/tests/ -v
```
Expected output: **32 passed in ~3.5s**.

