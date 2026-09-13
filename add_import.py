import sys
with open('frontend/app/orders/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

import_stmt = 'import ProductImage from "@/components/ProductImage";\n'
content = content.replace('import { Sparkles', import_stmt + 'import { Sparkles')

with open('frontend/app/orders/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
