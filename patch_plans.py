import os
path = 'frontend/app/plans/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'have_items: Array<{ item: string; stock: string; status: string }>;',
    'have_items: Array<{ item: string; stock: string; status: string; imageUrl?: string }>;'
)
content = content.replace(
    'need_items: Array<{ item: string; needed: string; estimated_price: number }>;',
    'need_items: Array<{ item: string; needed: string; estimated_price: number; imageUrl?: string }>;'
)

# Add import
if 'import ProductImage' not in content:
    content = content.replace('import Link from "next/link";', 'import Link from "next/link";\nimport ProductImage from "@/components/ProductImage";')

# Add to have_items
content = content.replace(
    '<Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 stroke-[3]" />\n                                <span>{h.item}</span>',
    '<Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 stroke-[3]" />\n                                {h.imageUrl && (\n                                  <ProductImage src={h.imageUrl} alt={h.item} width={16} height={16} className="w-4 h-4 bg-transparent" />\n                                )}\n                                <span>{h.item}</span>'
)

# Add to need_items
content = content.replace(
    '<div className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />\n                                    <span>{n.item}</span>',
    '<div className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />\n                                    {n.imageUrl && (\n                                      <ProductImage src={n.imageUrl} alt={n.item} width={16} height={16} className="w-4 h-4 bg-transparent" />\n                                    )}\n                                    <span>{n.item}</span>'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
