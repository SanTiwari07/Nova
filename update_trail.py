import sys

with open('frontend/app/orders/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Just replace the specific paragraphs
old_p = '''                      <p className="text-sm text-neutral-800 font-medium truncate">{entry.product}</p>
                      {entry.reasons[0] && (
                        <p className="text-xs text-neutral-500 mt-0.5 line-clamp-1">{entry.reasons[0]}</p>
                      )}'''

new_p = '''                      <div className="flex items-center gap-3 mt-1.5">
                        {entry.imageUrl ? (
                          <div className="w-12 h-12 shrink-0 border border-neutral-100 rounded-lg overflow-hidden bg-white relative">
                            <ProductImage src={entry.imageUrl} alt={entry.product} className="object-contain p-1" fill sizes="48px" />
                          </div>
                        ) : null}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-neutral-800 font-medium truncate">{entry.product}</p>
                          {entry.reasons[0] && (
                            <p className="text-xs text-neutral-500 mt-0.5 line-clamp-2">{entry.reasons[0]}</p>
                          )}
                        </div>
                      </div>'''

if old_p in content:
    content = content.replace(old_p, new_p)
    with open('frontend/app/orders/page.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced decision trail block.")
else:
    print("Could not find old_p block.")
