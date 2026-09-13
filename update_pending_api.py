import sys

with open('backend/api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_fn = '''def get_pending_orders():
    """Items awaiting explicit user approval (decision=ASK)."""
    audit_logs = audit_service.get_recent(limit=50)
    pending = [
        log for log in audit_logs
        if log.get("decision") == "ASK" and "APPROVED" not in log.get("decision", "") and "REJECTED" not in log.get("decision", "")
    ]
    return {"pending": pending, "count": len(pending)}'''

new_fn = '''def get_pending_orders():
    """Items awaiting explicit user approval (decision=ASK)."""
    audit_logs = audit_service.get_recent(limit=50)
    pending = [
        log for log in audit_logs
        if log.get("decision") == "ASK" and "APPROVED" not in log.get("decision", "") and "REJECTED" not in log.get("decision", "")
    ]
    for event in pending:
        if event.get("entityId"):
            prod = product_repo.get_by_id(event["entityId"])
            if prod and "imageUrl" in prod:
                event["imageUrl"] = prod["imageUrl"]
            elif prod and "image" in prod:
                event["imageUrl"] = prod["image"]
    return {"pending": pending, "count": len(pending)}'''

if old_fn in content:
    content = content.replace(old_fn, new_fn)
    with open('backend/api/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated get_pending_orders API")
else:
    print("Could not find get_pending_orders API block")
