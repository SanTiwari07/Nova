import os
path = 'backend/api/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'have_items.append({\n                    "item": comp["item"],',
    'have_items.append({\n                    "item": comp["item"], "imageUrl": _get_demo_image(comp["item"]) or _get_demo_image(matched_item["name"]) if "_get_demo_image" in globals() else None,'
)

content = content.replace(
    'need_items.append({\n                    "item": comp["item"],',
    'need_items.append({\n                    "item": comp["item"], "imageUrl": _get_demo_image(comp["item"]) if "_get_demo_image" in globals() else None,'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
