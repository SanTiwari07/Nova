import os
import glob
for root, _, files in os.walk(r'd:\Projects\Nova\frontend'):
    for f in files:
        if f.endswith('.tsx') or f.endswith('.ts'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if 'generic.webp' in content:
                        print(f'Found generic.webp in {path}')
            except:
                pass
