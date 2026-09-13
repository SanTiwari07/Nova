import sys

with open('frontend/app/orders/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_ui = '''                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-bold text-neutral-900 mb-1">{item.product}</p>
                      {item.reasons.map((r, i) => (
                        <p key={i} className="text-xs text-neutral-500 mb-0.5">{r}</p>
                      ))}
                      <p className="text-[10px] text-neutral-400 mt-1">{timeAgo(item.timestamp)}</p>
                    </div>
                  </div>'''

new_ui = '''                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-start gap-3">
                        {item.imageUrl && (
                          <div className="w-12 h-12 shrink-0 border border-amber-100 rounded-lg overflow-hidden bg-white relative">
                            <ProductImage src={item.imageUrl} alt={item.product} className="object-contain p-1" fill sizes="48px" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="font-bold text-neutral-900 mb-1">{item.product}</p>
                          {item.reasons.map((r, i) => (
                            <p key={i} className="text-xs text-neutral-500 mb-0.5 line-clamp-1">{r}</p>
                          ))}
                          <p className="text-[10px] text-neutral-400 mt-1">{timeAgo(item.timestamp)}</p>
                        </div>
                      </div>
                    </div>
                  </div>'''

if old_ui in content:
    content = content.replace(old_ui, new_ui)
    with open('frontend/app/orders/page.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated pending items UI")
else:
    print("Could not find pending items UI block")
