import re

with open('backend/api/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''@app.get("/api/audit/activity")
async def get_activity(
    filter: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieve recent household audit & activity timeline events."""
    events = audit_service.get_recent(limit=limit, filter_type=filter)
    for event in events:
        if event.get("entityId"):
            prod = product_repo.get_by_id(event["entityId"])
            if prod and "imageUrl" in prod:
                event["imageUrl"] = prod["imageUrl"]
            elif prod and "image" in prod:
                event["imageUrl"] = prod["image"]
    return events'''

# More robust regex or simple string replacement
old_str = '''@app.get("/api/audit/activity")
async def get_activity(
    filter: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieve recent household audit & activity timeline events."""
    return audit_service.get_recent(limit=limit, filter_type=filter)'''

if old_str in content:
    content = content.replace(old_str, replacement)
else:
    print("WARNING: Could not find exact string match.")

with open('backend/api/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
