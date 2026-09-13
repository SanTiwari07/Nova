import sys
sys.path.insert(0, "backend")
from images.image_validator import validate_image_url

urls = [
    ("Tata Tea", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8885b54a-f2b1-4f36-9a25-c64ef5ec3110_S02C3U191A_MN_18122025.png"),
    ("Dals", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/769d0d34-4b53-48e0-bb15-08e8b61c940d_UUP2C7X8N6_MN_18022026.png"),
    ("Parle-G", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/3ea49925-5e60-4966-9ef0-bbcb9935bfbb_B229F84CFF_MN_18022026.png"),
    ("Dahi", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/5/6/c158f160-5539-4c68-957f-117208fc48a4_NPI-132551_1_20260506_074805.png"),
    ("Drinks", "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/43ae9df1-80a2-4a00-9941-89ce86d9a440_38407_1.png"),
]

for label, u in urls:
    valid, reason, dims = validate_image_url(u)
    print(f"{label}: valid={valid}, dims={dims}, reason={reason}")
