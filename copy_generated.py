import os
import shutil
import glob

brain_dir = r'C:\Users\sansk\.gemini\antigravity\brain\61c18a14-2819-4fa2-9ce1-a81492b28075'
dest_dir = r'd:\Projects\Nova\backend\assets\fallbacks'

images = glob.glob(os.path.join(brain_dir, 'cat_*.png'))
for img in images:
    # e.g. cat_atta_123.png -> atta
    base = os.path.basename(img)
    parts = base.split('_')
    cat_name = parts[1]
    
    dest_path = os.path.join(dest_dir, f'{cat_name}.png')
    shutil.copyfile(img, dest_path)
    print(f'Copied {img} to {dest_path}')
