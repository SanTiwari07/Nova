import json
import os
import random

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

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
    "Shampoo": ["Sunsilk", "Clinic Plus", "Head & Shoulders", "Pantene"],
    "Deodorant": ["Nivea", "Axe", "Engage", "Fogg"],
    "Snacks": ["Haldiram's", "Lays", "Kurkure", "Bingo"]
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
    "Shampoo": ["Anti-Dandruff", "Hair Fall Rescue", "Silky Black", "Long & Strong"],
    "Deodorant": ["Fresh", "Sport", "Cool", "Intense"],
    "Snacks": ["Salted", "Masala", "Tomato", "Cheese"]
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
    "Shampoo": ["180 ml", "340 ml", "650 ml"],
    "Deodorant": ["150 ml", "200 ml"],
    "Snacks": ["50 g", "100 g", "200 g"]
}

# Base Prices
BASE_PRICES = {
    "Rice": 150, "Atta": 50, "Oil": 180, "Salt": 25, "Sugar": 50,
    "Spices": 60, "Noodles": 15, "Biscuits": 30, "Milk": 60, "Tea": 150,
    "Coffee": 200, "Detergent": 120, "Dishwash": 60, "Soap": 40,
    "Toothpaste": 80, "Shampoo": 150, "Deodorant": 200, "Snacks": 20
}

COLORS = ["#f8fafc", "#f0fdf4", "#fffbeb", "#fef2f2", "#fdf4ff", "#faf5ff"]

def generate_image(text, filepath, size=(800, 800), bg_color="#ffffff", text_color="#333333"):
    if not HAS_PIL:
        # Create a dummy file just to satisfy existence if PIL is missing
        with open(filepath, 'wb') as f:
            f.write(b"DUMMY_IMAGE_DATA")
        return
    
    img = Image.new('RGB', size, color=bg_color)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 15:
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        lines.append(" ".join(current_line))
        
    y_text = size[1] / 3
    for line in lines:
        d.text((size[0]/4, y_text), line, fill=text_color, font=font)
        y_text += 20
        
    img.save(filepath, format="WEBP", quality=80)

def generate_catalog():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets", "products")
    catalog_dir = os.path.join(base_dir, "catalog")
    
    os.makedirs(catalog_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    
    fallbacks_dir = os.path.join(base_dir, "assets", "fallbacks")
    os.makedirs(fallbacks_dir, exist_ok=True)
    
    products = []
    pid_counter = 1
    
    print("Generating products and assets...")
    
    for category in BRANDS.keys():
        cat_dir = os.path.join(assets_dir, category.lower())
        os.makedirs(cat_dir, exist_ok=True)
        
        fallback_path = os.path.join(fallbacks_dir, f"{category.lower()}.webp")
        generate_image(f"{category} Fallback", fallback_path, bg_color="#e2e8f0")
        
        for brand in BRANDS[category]:
            for variant in VARIANTS[category]:
                for pack_size in PACK_SIZES[category]:
                    
                    product_id = f"prod_{pid_counter:06d}"
                    pid_counter += 1
                    
                    name = f"{brand} {variant} {category}"
                    
                    sku_brand = brand.replace(" ", "").upper()[:4]
                    sku_cat = category.upper()[:4]
                    sku = f"NOVA-{sku_cat}-{sku_brand}-{pid_counter:04d}"
                    
                    multiplier = 1.0
                    if "5 kg" in pack_size or "5 L" in pack_size: multiplier = 4.5
                    elif "10 kg" in pack_size: multiplier = 9.0
                    elif "500 g" in pack_size or "500 ml" in pack_size: multiplier = 0.6
                    elif "250" in pack_size: multiplier = 0.3
                    elif "100" in pack_size or "Pack" in pack_size: multiplier = 0.15
                    elif "50" in pack_size: multiplier = 0.08
                    
                    price = int(BASE_PRICES[category] * multiplier * random.uniform(0.9, 1.2))
                    
                    image_filename = f"{product_id}.webp"
                    image_rel_path = f"/assets/products/{category.lower()}/{image_filename}"
                    image_abs_path = os.path.join(cat_dir, image_filename)
                    
                    bg_color = random.choice(COLORS)
                    generate_image(f"{name}\n{pack_size}", image_abs_path, bg_color=bg_color)
                    
                    product = {
                        "id": product_id,
                        "sku": sku,
                        "name": f"{name} {pack_size}",
                        "brand": brand,
                        "category": category,
                        "subcategory": variant,
                        "description": f"Premium {category.lower()} for everyday household use.",
                        "image": image_rel_path,
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
                        "provider_product_id": f"demo_{product_id}",
                        "asset_status": "verified"
                    }
                    
                    products.append(product)
                    
    generic_fallback_path = os.path.join(fallbacks_dir, "generic.webp")
    generate_image("Generic Product", generic_fallback_path, bg_color="#cbd5e1")
    
    out_path = os.path.join(catalog_dir, "products.json")
    with open(out_path, "w") as f:
        json.dump(products, f, indent=2)
        
    print(f"Successfully generated {len(products)} products and assets in {out_path}")

if __name__ == "__main__":
    generate_catalog()
