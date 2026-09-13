import sys
with open('frontend/app/orders/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'qty?: number;\n}', 
    'qty?: number;\n  imageUrl?: string;\n}'
)

content = content.replace(
    'timestamp: string;\n}', 
    'timestamp: string;\n  imageUrl?: string;\n}'
)

with open('frontend/app/orders/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
