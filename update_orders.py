import sys

with open('frontend/app/orders/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_list = '''                      <div className="flex flex-wrap gap-1 mb-2">
                        {(order.items || []).slice(0, 3).map((item, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-600">
                            {item.name}
                          </span>
                        ))}
                        {(order.items?.length ?? 0) > 3 && (
                          <span className="text-xs px-2 py-0.5 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-400">
                            +{(order.items?.length ?? 0) - 3} more
                          </span>
                        )}
                      </div>'''

new_list = '''                      <div className="flex flex-wrap gap-1.5 mb-2">
                        {(order.items || []).slice(0, 3).map((item, i) => (
                          <div key={i} className="flex items-center gap-1.5 text-xs pr-2 py-0.5 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-600 overflow-hidden">
                            {item.imageUrl ? (
                              <div className="w-5 h-5 shrink-0 bg-white border-r border-neutral-100 relative">
                                <ProductImage src={item.imageUrl} alt={item.name} className="object-contain p-0.5" fill sizes="20px" />
                              </div>
                            ) : (
                              <div className="w-1.5" />
                            )}
                            <span className={item.imageUrl ? "" : "pl-0.5"}>{item.name}</span>
                          </div>
                        ))}
                        {(order.items?.length ?? 0) > 3 && (
                          <span className="text-xs px-2 py-1 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-400 flex items-center">
                            +{(order.items?.length ?? 0) - 3} more
                          </span>
                        )}
                      </div>'''

if old_list in content:
    content = content.replace(old_list, new_list)
    print("Replaced tags block")
else:
    print("Could not find tags block")

old_expanded = '''                        {(order.items || []).map((item, i) => (
                          <div key={i} className="flex items-center justify-between py-2 border-t border-amber-100/50">
                            <p className="text-sm text-neutral-700">{item.name}</p>
                            <p className="text-sm font-bold text-neutral-900">₹{item.price}</p>
                          </div>
                        ))}'''

new_expanded = '''                        <div className="mt-3 space-y-2">
                          {(order.items || []).map((item, i) => (
                            <div key={i} className="flex items-center justify-between py-2 border-t border-amber-100/50">
                              <div className="flex items-center gap-3">
                                {item.imageUrl && (
                                  <div className="w-10 h-10 shrink-0 border border-neutral-100 rounded bg-white relative overflow-hidden">
                                    <ProductImage src={item.imageUrl} alt={item.name} className="object-contain p-1" fill sizes="40px" />
                                  </div>
                                )}
                                <p className="text-sm text-neutral-700 font-medium">{item.name} <span className="text-neutral-400">x{item.qty || 1}</span></p>
                              </div>
                              <p className="text-sm font-bold text-neutral-900">₹{item.price}</p>
                            </div>
                          ))}
                        </div>'''

if old_expanded in content:
    content = content.replace(old_expanded, new_expanded)
    print("Replaced expanded block")
else:
    print("Could not find expanded block")

with open('frontend/app/orders/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
