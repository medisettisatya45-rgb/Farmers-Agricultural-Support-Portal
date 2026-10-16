
import os
import sqlite3
import re

# Configuration
IMAGE_DIR = 'static/images/products'
DB_PATH = 'database/agriculture.db'

# Keyword mapping for categorization
CATEGORY_KEYWORDS = {
    'Fruit': ['apple', 'orange', 'grape', 'mango', 'banana', 'papaya', 'pomegranate', 'pineapple', 'watermelon', 'melon', 'berry', 'cherry', 'fruit', 'lemon', 'lime', 'citrus', 'avocado'],
    'Vegetable': ['tomato', 'potato', 'onion', 'carrot', 'cabbage', 'cauliflower', 'spinach', 'brinjal', 'eggplant', 'pepper', 'chili', 'capsicum', 'cucumber', 'gourd', 'okra', 'ladyfinger', 'bean', 'pea', 'vegetable', 'veg', 'pumpkin', 'corn', 'maize', 'ginger', 'garlic', 'radish'],
    'Grain': ['rice', 'wheat', 'millets', 'jowar', 'bajra', 'ragi', 'flour', 'grain', 'pulse', 'dal', 'gram', 'lentil', 'cereal'],
    'Dairy': ['milk', 'cheese', 'butter', 'curd', 'ghee', 'paneer', 'yogurt'],
    'Spice': ['turmeric', 'chilli', 'spice', 'pepper', 'clove', 'cardamom', 'cinnamon']
}

DEFAULT_CATEGORY_ID = 4  # Vegetables (Fallback)
USER_ID = 1  # Admin/System user

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def detect_info_from_filename(filename):
    name = os.path.splitext(filename)[0]
    
    # Check if name is a has/junk (32 hex text)
    if re.match(r'^[a-f0-9]{32}$', name):
        return None # Skip hash filenames
        
    # Remove junk like "removebg", "preview", numbers, common prefixes
    name = re.sub(r'[-_]removebg', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[-_]preview', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[-_]?image[-_]?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'pngtree', '', name, flags=re.IGNORECASE)
    name = re.sub(r'istockphoto', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[0-9]+', '', name) # Remove numbers
    name = re.sub(r'[-_]', ' ', name) # Replace separators with spaces
    
    # Remove common adjectives to get "original name"
    adjectives = [r'\bfresh\b', r'\borganic\b', r'\bsweet\b', r'\bwhole\b', r'\bhot\b', r'\bgreen\b', r'\bred\b', r'\byellow\b', r'\braw\b']
    for adj in adjectives:
        name = re.sub(adj, '', name, flags=re.IGNORECASE)
        
    name = re.sub(r'\s+', ' ', name).strip() # Clean extra spaces
    
    if len(name) < 3 or name.lower() == 'img': return None # Too short after cleaning or just 'Img'
    
    # Capitalize
    product_name = name.title()
    
    # Specific corrections
    if 'Potato' in product_name: product_name = 'Potato'
    if 'Tomato' in product_name: product_name = 'Tomato'
    if 'Onion' in product_name: product_name = 'Onion'
    if 'Cauliflower' in product_name: product_name = 'Cauliflower'
    if 'Corn' in product_name: product_name = 'Corn'
    if 'Pumpkin' in product_name: product_name = 'Pumpkin'
    if 'Avocado' in product_name: product_name = 'Avocado'
    
    return product_name

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = get_db_connection()
    
    # 1. Fetch Categories
    categories = conn.execute('SELECT category_id, name FROM categories').fetchall()
    cat_map = {row['name'].lower(): row['category_id'] for row in categories}
    print(f"Loaded {len(categories)} categories.")

    # Helper to find category ID
    def find_category_id(prod_name):
        prod_lower = prod_name.lower()
        for cat_name, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in prod_lower:
                    # Find matching DB category
                    for db_cat, db_id in cat_map.items():
                        if cat_name.lower() in db_cat:
                            return db_id
                        # Fallback: if keyword matches db category name directly
                        if kw in db_cat:
                             return db_id
        return DEFAULT_CATEGORY_ID

    # 2. Scan Images
    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory not found at {IMAGE_DIR}")
        return

    image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    print(f"Found {len(image_files)} images.")

    # 3. Check existing products/images to avoid duplicates
    existing_images = set()
    rows = conn.execute('SELECT image_url FROM products').fetchall()
    for r in rows:
        if r['image_url']:
            existing_images.add(os.path.basename(r['image_url']))
            
    rows_imgs = conn.execute('SELECT image_url FROM product_images').fetchall()
    for r in rows_imgs:
         if r['image_url']:
            existing_images.add(os.path.basename(r['image_url']))

    added_count = 0
    
    for img_file in image_files:
        if img_file in existing_images:
            continue
            
        # Detect Name
        product_name = detect_info_from_filename(img_file)
        if not product_name or len(product_name) < 3: # Skip junk names
            # print(f"Skipping junk name for {img_file}")
            continue
            
        # Check if product name already exists (to avoid duplicate "Tomato" etc)
        existing_prod = conn.execute('SELECT product_id FROM products WHERE name = ?', (product_name,)).fetchone()
        
        if existing_prod:
            # If it exists, we might want to ensure the image is linked?
            # For now, just skip to avoid duplicates
            continue

        # Determine Category
        cat_id = find_category_id(product_name)
        
        # Determine Price
        price = 40.0 # Default
        if cat_id == cat_map.get('fruits', 1): price = 120.0
        elif cat_id == cat_map.get('grains', 2): price = 60.0
        
        # Insert Product
        image_url = f"/static/images/products/{img_file}"
        
        try:
            cursor = conn.execute('''
                INSERT INTO products (name, description, price, category_id, user_id, image_url, stock_quantity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_name, f"Fresh {product_name} from local farms.", price, cat_id, USER_ID, image_url, 100))
            
            product_id = cursor.lastrowid
            
            # Insert into product_images too for gallery
            conn.execute('''
                INSERT INTO product_images (product_id, image_url, image_order)
                VALUES (?, ?, ?)
            ''', (product_id, image_url, 0))
            
            print(f"Added: {product_name} | Image: {img_file}")
            added_count += 1
            
        except Exception as e:
            print(f"Error adding {product_name}: {e}")

    conn.commit()
    conn.close()
    print(f"Successfully added {added_count} new products.")

if __name__ == '__main__':
    main()
