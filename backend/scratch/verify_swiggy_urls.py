import sys
sys.path.insert(0, "backend")
from images.image_validator import validate_image_url

urls = [
    ("Atta", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/3/9/805a02b1-e08b-4d4b-aa8f-ab05cabb1e37_1780_1.png"),
    ("Rice", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/7/21/ed973afb-e397-4df3-8a23-6153474d93b0_450_1.png"),
    ("Oil", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png"),
    ("Milk", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png"),
    ("Noodles", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"),
    ("Salt", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png"),
    ("Surf", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/594241ca-83c8-47c0-82a1-12c8b87455d3_8901030843150_MN_18022026.png"),
]

for label, u in urls:
    valid, reason, dims = validate_image_url(u)
    print(f"{label}: valid={valid}, dims={dims}, reason={reason}")
