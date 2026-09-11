import json
import os
import uuid
import random

# Realistic Indian Brands mapped to Categories
BRANDS = {
    "Rice": ["India Gate", "Daawat", "Kohinoor", "Fortune"],
    "Atta": ["Aashirvaad", "Pillsbury", "Fortune", "Nature Fresh"],
    "Oil": ["Fortune", "Saffola", "Dhara", "Sundrop"],
    "Salt": ["Tata", "Aashirvaad", "Catch"],
    "Sugar": ["Madhur", "Parry's", "Trust"],
    "Spices": ["Everest", "MDH", "Catch", "Suhana"],
    "Noodles": ["Maggi", "Yippee", "Top Ramen", "Ching's"],
    "Biscuits": ["Parle", "Britannia", "Sunfeast", "Priyagold"],
    "Milk": ["Amul", "Mother Dairy", "Nandini", "Gowardhan"],
    "Tea": ["Tata Tea", "Brooke Bond", "Wagh Bakri", "Lipton"],
    "Coffee": ["Bru", "Nescafe", "Davidoff", "Tata Coffee"],
    "Detergent": ["Surf Excel", "Ariel", "Tide", "Rin"],
    "Dishwash": ["Vim", "Pril", "Exo"],
    "Soap": ["Dove", "Lux", "Pears", "Cinthol"],
    "Toothpaste": ["Colgate", "Pepsodent", "Sensodyne", "Close Up"],
    "Shampoo": ["Sunsilk", "Clinic Plus", "Head & Shoulders", "Pantene"]
}

# Subcategories / Variants
VARIANTS = {
    "Rice": ["Basmati", "Sona Masoori", "Brown Rice", "Wada Kolam"],
    "Atta": ["Whole Wheat", "Multigrain", "Chakki Fresh"],
    "Oil": ["Sunflower", "Mustard", "Soyabean", "Groundnut"],
    "Salt": ["Iodized", "Pink Rock Salt", "Crystal"],
    "Sugar": ["Refined", "Brown Sugar", "Cube Sugar"],
    "Spices": ["Turmeric", "Red Chilli", "Coriander", "Garam Masala", "Cumin"],
    "Noodles": ["Masala", "Chicken", "Atta", "Oats"],
    "Biscuits": ["Marie", "Bourbon", "Glucose", "Cream", "Digestive"],
    "Milk": ["Taaza", "Gold", "Cow", "Toned"],
    "Tea": ["Premium", "Green Tea", "Masala Chai", "Gold"],
    "Coffee": ["Instant", "Filter", "Espresso", "Gold"],
    "Detergent": ["Matic Front Load", "Matic Top Load", "Easy Wash", "Liquid"],
    "Dishwash": ["Liquid", "Bar", "Gel"],
    "Soap": ["Beauty Bar", "Glycerine", "Sandalwood", "Neem"],
    "Toothpaste": ["Active Salt", "Total", "Whitening", "Herbal"],
    "Shampoo": ["Anti-Dandruff", "Hair Fall Rescue", "Silky Black", "Long & Strong"]
}

# Pack Sizes
PACK_SIZES = {
    "Rice": ["1 kg", "5 kg", "10 kg"],
    "Atta": ["1 kg", "5 kg", "10 kg"],
    "Oil": ["1 L", "5 L"],
    "Salt": ["500 g", "1 kg"],
    "Sugar": ["1 kg", "5 kg"],
    "Spices": ["100 g", "250 g", "500 g"],
    "Noodles": ["70 g", "280 g (4 Pack)", "420 g (6 Pack)"],
    "Biscuits": ["100 g", "250 g", "500 g"],
    "Milk": ["500 ml", "1 L"],
    "Tea": ["250 g", "500 g", "1 kg"],
    "Coffee": ["50 g", "100 g", "200 g"],
    "Detergent": ["500 g", "1 kg", "2 kg", "1 L Liquid"],
    "Dishwash": ["250 ml", "500 ml", "300 g Bar"],
    "Soap": ["75 g", "100 g", "125 g (3 Pack)"],
    "Toothpaste": ["100 g", "200 g"],
    "Shampoo": ["180 ml", "340 ml", "650 ml"]
}

# Base Prices (approximate)
BASE_PRICES = {
    "Rice": 150, "Atta": 50, "Oil": 180, "Salt": 25, "Sugar": 50,
    "Spices": 60, "Noodles": 15, "Biscuits": 30, "Milk": 60, "Tea": 150,
    "Coffee": 200, "Detergent": 120, "Dishwash": 60, "Soap": 40,
    "Toothpaste": 80, "Shampoo": 150
}

def generate_products():
    products = []
    pid_counter = 1
    
    for category in BRANDS.keys():
        for brand in BRANDS[category]:
            for variant in VARIANTS[category]:
                for pack_size in PACK_SIZES[category]:
                    
                    product_id = f"prod_{pid_counter:06d}"
                    pid_counter += 1
                    
                    name = f"{brand} {variant} {category} - {pack_size}"
                    
                    # Generate a plausible SKU
                    sku_brand = brand.replace(" ", "").upper()[:4]
                    sku_cat = category.upper()[:4]
                    sku = f"NOVA-{sku_cat}-{sku_brand}-{pid_counter:04d}"
                    
                    # Price calculation based on unit size rough multiplier
                    multiplier = 1.0
                    if "5 kg" in pack_size or "5 L" in pack_size: multiplier = 4.5
                    elif "10 kg" in pack_size: multiplier = 9.0
                    elif "500 g" in pack_size or "500 ml" in pack_size: multiplier = 0.6
                    elif "250" in pack_size: multiplier = 0.3
                    elif "100" in pack_size or "Pack" in pack_size: multiplier = 0.15
                    
                    # Add some randomness to price
                    price = int(BASE_PRICES[category] * multiplier * random.uniform(0.9, 1.2))
                    
                    # Generate standard image path
                    safe_name = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
                    image_path = f"/products/{category.lower()}/{safe_name}.webp"
                    
                    product = {
                        "id": product_id,
                        "sku": sku,
                        "name": name,
                        "brand": brand,
                        "category": category,
                        "subcategory": variant,
                        "description": f"Premium {category.lower()} for everyday household use.",
                        "image": image_path,
                        "price": max(10, price),
                        "currency": "INR",
                        "unit": "pack",
                        "pack_size": pack_size,
                        "availability": "IN_STOCK" if random.random() > 0.1 else "OUT_OF_STOCK",
                        "rating": round(random.uniform(3.5, 5.0), 1),
                        "review_count": random.randint(10, 5000),
                        "tags": [category.lower(), variant.lower(), "grocery"],
                        "preferred": random.random() > 0.8,
                        "provider": "nova_demo",
                        "provider_product_id": f"demo_{product_id}"
                    }
                    
                    products.append(product)
    
    # Save the catalog
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), "catalog.json")
    with open(out_path, "w") as f:
        json.dump(products, f, indent=2)
        
    print(f"Successfully generated {len(products)} products in {out_path}")

if __name__ == "__main__":
    generate_products()
