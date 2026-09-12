import urllib.request
import os

logos = {
    "Blinkit": "https://logo.clearbit.com/blinkit.com",
    "Zepto": "https://logo.clearbit.com/zeptonow.com",
    "Swiggy": "https://logo.clearbit.com/swiggy.com",
    "Zomato": "https://logo.clearbit.com/zomato.com",
    "BigBasket": "https://logo.clearbit.com/bigbasket.com",
    "Flipkart": "https://logo.clearbit.com/flipkart.com"
}

dest_dir = r"d:\Projects\Nova\frontend\public\logos"
os.makedirs(dest_dir, exist_ok=True)

for name, url in logos.items():
    dest_path = os.path.join(dest_dir, f"{name.lower()}.png")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Downloaded {name} logo")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
