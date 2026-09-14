import os
path = 'backend/api/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '\"have_items\": [\n            {\"name\": \"Cooking Oil\",': '\"have_items\": [\n            {\"name\": \"Cooking Oil\", \"imageUrl\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png\",',
    '{\"name\": \"Salt & Spices\", \"stock\"': '{\"name\": \"Salt & Spices\", \"imageUrl\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png\", \"stock\"',
    '\"need_items\": [\n            {\"name\": \"Maggi 2-Minute Masala Noodles (Pack of 4)\"': '\"need_items\": [\n            {\"name\": \"Maggi 2-Minute Masala Noodles (Pack of 4)\", \"imageUrl\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png\"'
}

for old, new in replacements.items():
    if old in content:
        content = content.replace(old, new)
        print("Replaced:", old[:30])

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
