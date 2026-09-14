import os
path = 'backend/api/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('@app.get("/api/household-status")\ndef _get_demo_image(prod_name):', 'def _get_demo_image(prod_name):')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
