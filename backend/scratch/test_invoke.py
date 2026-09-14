import os
import sys
import dotenv
dotenv.load_dotenv()

import asyncio
from api.main import nova_agent

async def test():
    print("Agent active_provider:", nova_agent.active_provider)
    print("Agent has agent object:", nova_agent.agent is not None)
    
    # Test handle_request
    print("\n--- Testing 'I want to make panipuri' ---")
    try:
        res = await asyncio.wait_for(nova_agent.handle_request("I want to make panipuri"), timeout=30.0)
        print("Status:", res.get("status"))
        print("Mode:", res.get("mode"))
        print("Provider:", res.get("provider"))
        print("Response:\n", res.get("response"))
        print("Tool trace:", [t.get("tool") for t in res.get("tool_trace", [])])
    except Exception as e:
        print("Error during handle_request:", type(e), e)

asyncio.run(test())
