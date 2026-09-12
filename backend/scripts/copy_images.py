import os
import shutil
import glob

brain_dir = r"C:\Users\sansk\.gemini\antigravity\brain\50048786-bed3-4594-b87b-71594423fae1"
dest_dir = r"d:\Projects\Nova\backend\assets\fallbacks"

mappings = {
    "milk_fallback": "milk.webp",
    "rice_fallback": "rice.webp",
    "oil_fallback": "oil.webp",
    "noodles_fallback": "noodles.webp",
    "hero_banner": "hero.webp"
}

for prefix, dest_name in mappings.items():
    matches = glob.glob(os.path.join(brain_dir, f"{prefix}_*.png"))
    if matches:
        latest = sorted(matches)[-1]
        dest_path = os.path.join(dest_dir, dest_name)
        shutil.copy2(latest, dest_path)
        print(f"Copied {latest} to {dest_path}")
    else:
        print(f"No match for {prefix}")
