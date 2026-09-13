import sys

with open('backend/api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_fn = '''def get_orders():
    raw_orders = commerce_adapter.get_orders()
    # Enrich with audit context
    audit_logs = audit_service.get_recent(limit=100)
    enriched = []
    for order in raw_orders:
        order_id = order.get("id", "")
        # Find matching audit log entry
        audit_entry = next(
            (log for log in audit_logs if order_id in log.get("product", "")), None
        )
        decision_raw = order.get("decision", "AUTO")
        enriched.append({
            **order,
            "decision_label": _DECISION_LABELS.get(decision_raw, decision_raw),
            "nova_reason": audit_entry["reasons"] if audit_entry else [
                f"Purchase placed via NOVA autopilot ({decision_raw})."
            ],
            "source": order.get("source", "AGENT"),
        })
    return enriched'''

new_fn = '''def get_orders():
    raw_orders = commerce_adapter.get_orders()
    # Enrich with audit context
    audit_logs = audit_service.get_recent(limit=100)
    enriched = []
    for order in raw_orders:
        order_id = order.get("id", "")
        # Find matching audit log entry
        audit_entry = next(
            (log for log in audit_logs if order_id in log.get("product", "")), None
        )
        decision_raw = order.get("decision", "AUTO")
        
        # Enrich items with images
        enriched_items = []
        for item in order.get("items", []):
            item_copy = dict(item)
            prod_id = item.get("id") or item.get("productId") or item.get("variantId")
            if prod_id:
                prod = product_repo.get_by_id(prod_id)
                if prod:
                    item_copy["imageUrl"] = prod.get("imageUrl") or prod.get("image")
            elif "imageUrl" not in item_copy and "image" in item_copy:
                item_copy["imageUrl"] = item_copy["image"]
            enriched_items.append(item_copy)
            
        enriched.append({
            **order,
            "items": enriched_items,
            "decision_label": _DECISION_LABELS.get(decision_raw, decision_raw),
            "nova_reason": audit_entry["reasons"] if audit_entry else [
                f"Purchase placed via NOVA autopilot ({decision_raw})."
            ],
            "source": order.get("source", "AGENT"),
        })
    return enriched'''

if old_fn in content:
    content = content.replace(old_fn, new_fn)
    with open('backend/api/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated get_orders API")
else:
    print("Could not find get_orders API block")
