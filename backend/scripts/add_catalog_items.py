import json
import os

catalog_path = os.path.join(os.path.dirname(__file__), "..", "catalog", "products.json")

new_items = [
    {
        "id": "prod_000160",
        "sku": "NOVA-SNAK-HALD-0160",
        "name": "Haldiram's Minute Khana Pani Puri Pack 240g",
        "title": "Haldiram's Minute Khana Pani Puri Pack 240g (with Puri & Mint Water Paste)",
        "brand": "Haldiram's",
        "category": "Snacks & Biscuits",
        "subcategory": "Snacks",
        "price": 65,
        "mrp": 75,
        "currency": "INR",
        "unit": "pack",
        "pack_size": "240 g",
        "availability": "IN_STOCK",
        "tags": ["puri", "pani puri", "pani puri shells", "snack", "golgappa"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png"],
        "imageStatus": "found",
        "imageSource": "catalog"
    },
    {
        "id": "prod_000161",
        "sku": "NOVA-DAL-TATA-0161",
        "name": "Tata Sampann White Chickpeas (Kabuli Chana) 500g",
        "title": "Tata Sampann White Chickpeas (Kabuli Chana) 500g",
        "brand": "Tata Sampann",
        "category": "Dal & Pulses",
        "subcategory": "Pulses & Lentils",
        "price": 88,
        "mrp": 98,
        "currency": "INR",
        "unit": "pack",
        "pack_size": "500 g",
        "availability": "IN_STOCK",
        "tags": ["chana", "chickpeas", "kabuli chana", "dal", "pulses"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/16/eda40bda-ba3b-4fab-97ba-ccbd28c106cf_K71D7X8L8P_MN_15122025.png",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/16/eda40bda-ba3b-4fab-97ba-ccbd28c106cf_K71D7X8L8P_MN_15122025.png",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/16/eda40bda-ba3b-4fab-97ba-ccbd28c106cf_K71D7X8L8P_MN_15122025.png"],
        "imageStatus": "found",
        "imageSource": "catalog"
    },
    {
        "id": "prod_000162",
        "sku": "NOVA-SPIC-EVER-0162",
        "name": "Everest Pani Puri Masala 100g",
        "title": "Everest Pani Puri Masala Powder 100g",
        "brand": "Everest",
        "category": "Tea & Staples",
        "subcategory": "Spices",
        "price": 45,
        "mrp": 50,
        "currency": "INR",
        "unit": "pack",
        "pack_size": "100 g",
        "availability": "IN_STOCK",
        "tags": ["masala", "pani puri masala", "spices", "seasoning"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png"],
        "imageStatus": "found",
        "imageSource": "catalog"
    },
    {
        "id": "prod_000163",
        "sku": "NOVA-PAST-BAMB-0163",
        "name": "Bambino Macaroni Pasta 500g",
        "title": "Bambino Durum Wheat Macaroni Pasta 500g",
        "brand": "Bambino",
        "category": "Instant Noodles",
        "subcategory": "Pasta & Macaroni",
        "price": 48,
        "mrp": 55,
        "currency": "INR",
        "unit": "pack",
        "pack_size": "500 g",
        "availability": "IN_STOCK",
        "tags": ["pasta", "macaroni", "penne", "noodles", "italian"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"],
        "imageStatus": "found",
        "imageSource": "catalog"
    },
    {
        "id": "prod_000164",
        "sku": "NOVA-SAUC-VEEB-0164",
        "name": "Veeba Pasta & Pizza Sauce 350g",
        "title": "Veeba Italian Herb Pasta & Pizza Sauce 350g",
        "brand": "Veeba",
        "category": "Instant Noodles",
        "subcategory": "Pasta & Macaroni",
        "price": 89,
        "mrp": 99,
        "currency": "INR",
        "unit": "bottle",
        "pack_size": "350 g",
        "availability": "IN_STOCK",
        "tags": ["sauce", "pasta sauce", "pizza sauce", "pasta", "tomato sauce"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"],
        "imageStatus": "found",
        "imageSource": "catalog"
    },
    {
        "id": "prod_000165",
        "sku": "NOVA-DAIR-AMUL-0165",
        "name": "Amul Diced Mozzarella & Cheddar Cheese Blend 200g",
        "title": "Amul Diced Pizza Cheese Blend 200g",
        "brand": "Amul",
        "category": "Milk & Dairy",
        "subcategory": "Cheese",
        "price": 125,
        "mrp": 140,
        "currency": "INR",
        "unit": "pack",
        "pack_size": "200 g",
        "availability": "IN_STOCK",
        "tags": ["cheese", "mozzarella", "pizza cheese", "dairy"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png"],
        "imageStatus": "found",
        "imageSource": "catalog"
    },
    {
        "id": "prod_000166",
        "sku": "NOVA-VEGG-FRES-0166",
        "name": "Fresh Potato (Batata) 1kg",
        "title": "Farm Fresh Potatoes 1kg",
        "brand": "Fresh Produce",
        "category": "Tea & Staples",
        "subcategory": "Fresh Staples",
        "price": 35,
        "mrp": 40,
        "currency": "INR",
        "unit": "kg",
        "pack_size": "1 kg",
        "availability": "IN_STOCK",
        "tags": ["potato", "potatoes", "batata", "veggie", "vegetable"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/6/22/15eaf57e-e20f-4baf-a968-cbd6aaaf4b7a_94788_1.jpg",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/6/22/15eaf57e-e20f-4baf-a968-cbd6aaaf4b7a_94788_1.jpg",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/6/22/15eaf57e-e20f-4baf-a968-cbd6aaaf4b7a_94788_1.jpg"],
        "imageStatus": "found",
        "imageSource": "catalog"
    },
    {
        "id": "prod_000167",
        "sku": "NOVA-SPIC-EVER-0167",
        "name": "Everest Shahi Biryani Masala 50g",
        "title": "Everest Shahi Biryani Masala 50g",
        "brand": "Everest",
        "category": "Tea & Staples",
        "subcategory": "Spices",
        "price": 48,
        "mrp": 55,
        "currency": "INR",
        "unit": "pack",
        "pack_size": "50 g",
        "availability": "IN_STOCK",
        "tags": ["biryani masala", "masala", "spices", "biryani"],
        "preferred": True,
        "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png",
        "image": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png",
        "images": ["https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/8b5ecd2b-098a-4431-8a66-990cdf120314_04USQLUCHZ_MN_18122025.png"],
        "imageStatus": "found",
        "imageSource": "catalog"
    }
]

with open(catalog_path, "r", encoding="utf-8") as f:
    products = json.load(f)

existing_ids = {p["id"] for p in products}
added = 0
for item in new_items:
    if item["id"] not in existing_ids:
        products.append(item)
        existing_ids.add(item["id"])
        added += 1

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f"Successfully added {added} new catalog items. Total now: {len(products)}")
