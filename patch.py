import os
path = 'backend/inventory/inventory_service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '\"name\": \"Amul Taaza Milk 1L\",\n        \"image\": None,': '\"name\": \"Amul Taaza Milk 1L\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png\",',
    '\"name\": \"Fortune Sunflower Oil 5L\",\n        \"image\": None,': '\"name\": \"Fortune Sunflower Oil 5L\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png\",',
    '\"name\": \"India Gate Basmati Rice 5kg\",\n        \"image\": None,': '\"name\": \"India Gate Basmati Rice 5kg\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/7/21/ed973afb-e397-4df3-8a23-6153474d93b0_450_1.png\",',
    '\"name\": \"Aashirvaad Whole Wheat Atta 5kg\",\n        \"image\": None,': '\"name\": \"Aashirvaad Whole Wheat Atta 5kg\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/3/9/805a02b1-e08b-4d4b-aa8f-ab05cabb1e37_1780_1.png\",',
    '\"name\": \"Tata Salt 1kg\",\n        \"image\": None,': '\"name\": \"Tata Salt 1kg\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png\",',
    '\"name\": \"Tata Sampann Toor Dal 1kg\",\n        \"image\": None,': '\"name\": \"Tata Sampann Toor Dal 1kg\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/16/eda40bda-ba3b-4fab-97ba-ccbd28c106cf_K71D7X8L8P_MN_15122025.png\",',
    '\"name\": \"Tata Tea Gold 500g\",\n        \"image\": None,': '\"name\": \"Tata Tea Gold 500g\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/bf79f8d0-dfcb-4ebb-be63-b3e291656666_Q5AIG72TKQ_MN_18022026.png\",'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
