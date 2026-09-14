import os
path = 'backend/inventory/inventory_service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    '\"name\": \"Surf Excel Matic Front Load Detergent 2kg\",\n        \"image\": None,': '\"name\": \"Surf Excel Matic Front Load Detergent 2kg\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto/NI_CATALOG/IMAGES/CIW/2026/2/25/c9e9b048-c2b3-4f99-9ea2-2253adfc2b60_1.png\",',
    '\"name\": \"Madhur Pure & Hygienic Sugar 5kg\",\n        \"image\": None,': '\"name\": \"Madhur Pure & Hygienic Sugar 5kg\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto/NI_CATALOG/IMAGES/CIW/2026/2/25/c9e9b048-c2b3-4f99-9ea2-2253adfc2b60_2.png\",',
    '\"name\": \"Dettol Original Soap Pack of 4\",\n        \"image\": None,': '\"name\": \"Dettol Original Soap Pack of 4\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto/NI_CATALOG/IMAGES/CIW/2026/2/25/c9e9b048-c2b3-4f99-9ea2-2253adfc2b60_3.png\",',
    '\"name\": \"Harpic Power Plus Toilet Cleaner 1L\",\n        \"image\": None,': '\"name\": \"Harpic Power Plus Toilet Cleaner 1L\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto/NI_CATALOG/IMAGES/CIW/2026/2/25/c9e9b048-c2b3-4f99-9ea2-2253adfc2b60_4.png\",',
    '\"name\": \"Head & Shoulders Shampoo 340ml\",\n        \"image\": None,': '\"name\": \"Head & Shoulders Shampoo 340ml\",\n        \"image\": \"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto/NI_CATALOG/IMAGES/CIW/2026/2/25/c9e9b048-c2b3-4f99-9ea2-2253adfc2b60_5.png\",'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
