# NOVA Local Development and Deployment Setup

## 1. Zero-Cost-First Strategy
Development prioritizes local environments, mock commerce, seed data, and controlled AWS usage. We avoid provisioning expensive always-on infrastructure just for demonstration.

## 2. Environment Setup

### Backend (Python/FastAPI)
1. Navigate to `backend/`
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment.
4. Install dependencies: `pip install -r requirements.txt` (to be created)
5. Copy `.env.example` to `.env` and configure:
   - `AWS_PROFILE` (for Bedrock/DynamoDB local testing)
   - `COMMERCE_PROVIDER=mock`
6. Run the server: `uvicorn api.app:app --reload`

### Frontend (Next.js)
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Copy `.env.example` to `.env.local`
4. Run the development server: `npm run dev`

## 3. Mock Data
- Use `scripts/seed_household.py` to populate local DynamoDB or in-memory mock data with the default "Demo Household".
- The mock commerce adapter will simulate network latency and return success payloads for checkout.

## 4. AWS Deployment (Phase 2)
- Use AWS SAM or CDK to deploy the serverless stack (API Gateway + Lambda for backend, DynamoDB tables, EventBridge rules).
- Frontend deployed to Vercel or AWS Amplify.
