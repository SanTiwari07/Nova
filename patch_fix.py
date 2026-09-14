import os
path = 'backend/api/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('async \ndef _get_demo', 'def _get_demo')
content = content.replace('@app.get(\"/api/household\")\ndef get_household_status():', '@app.get(\"/api/household-status\")\nasync def get_household_status():')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
