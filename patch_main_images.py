import os
path = 'backend/api/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

mapping_snippet = '''
def _get_demo_image(prod_name):
    lower_name = prod_name.lower()
    if "milk" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png"
    if "oil" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png"
    if "maggi" in lower_name or "noodles" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"
    if "atta" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/3/9/805a02b1-e08b-4d4b-aa8f-ab05cabb1e37_1780_1.png"
    if "tea" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/bf79f8d0-dfcb-4ebb-be63-b3e291656666_Q5AIG72TKQ_MN_18022026.png"
    if "salt" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png"
    if "rice" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/7/21/ed973afb-e397-4df3-8a23-6153474d93b0_450_1.png"
    return None
'''

if 'def _get_demo_image' not in content:
    content = content.replace('def get_household_status():', mapping_snippet + '\n@app.get("/api/household")\ndef get_household_status():')

content = content.replace('\"system_telemetry\": {', '\"imageUrl\": _get_demo_image(prod_name),\n              \"system_telemetry\": {')
content = content.replace('\"system_telemetry\": {', '\"imageUrl\": _get_demo_image(act.get(\"product\", \"\")),\n              \"system_telemetry\": {')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
