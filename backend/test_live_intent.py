import asyncio
import os
from intent.intent_service import IntentReconciliationService
from inventory.inventory_service import InventoryService
from ai.ai_service import AIService

async def run():
    inv = InventoryService()
    ai = AIService()
    svc = IntentReconciliationService(inventory_service=inv, ai_service=ai)
    res = await svc.reconcile_intent("I want to make chicken curry for 4 people")
    print(res)

if __name__ == "__main__":
    asyncio.run(run())
