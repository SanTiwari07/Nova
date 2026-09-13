import urllib.request
import urllib.error

urls = [
    "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/e0ba2bc8-41b9-45c8-86fc-15e40a497127_IPAQ07QO0C_MN_18022026.png",
    "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png",
    "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
}

for u in urls:
    req = urllib.request.Request(u, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            content_type = resp.headers.get("Content-Type")
            content_len = len(resp.read())
            print(f"URL: {u}")
            print(f"STATUS: {resp.status}, Content-Type: {content_type}, Length: {content_len} bytes")
    except Exception as e:
        print(f"FAILED URL {u}: {e}")
