import os
import sys
import asyncio
import dotenv
dotenv.load_dotenv()

from api.main import nova_agent

async def run_tests():
    tests = [
        ("TEST 1: Panipuri", "I want to make panipuri"),
        ("TEST 2: Pasta for 4", "I want to make pasta for four people"),
        ("TEST 3: Maggi", "I want to make Maggi tonight"),
        ("TEST 4: Direct Need (Milk)", "I need milk"),
        ("TEST 5: Restraint Check (Cooking Oil)", "Do I need cooking oil?"),
        ("TEST 6: Low Stock Inspection", "What's running low?"),
        ("TEST 7: Audit Explanation", "Why did you buy milk?"),
        ("TEST 8: Follow-up (Puri)", "Get the puri"),
    ]

    for title, prompt in tests:
        print(f"\n{'='*70}\n{title}: '{prompt}'\n{'='*70}")
        try:
            res = await nova_agent.handle_request(prompt)
            print(f"Status: {res.get('status')} | Mode: {res.get('mode')} | Provider: {res.get('provider')}")
            print(f"\nResponse:\n{res.get('response')}\n")
            tools = [t.get('tool') for t in res.get('tool_trace', [])]
            print(f"Tools Invoked: {tools}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
