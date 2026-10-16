import sqlite3
import os
import re

DB_PATH = 'database/agriculture.db'
IMAGE_DIR = 'static/images/products'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_name(name):
    # Lowercase
    n = name.lower()
    
    # Remove junk words
    junk = ['fresh', 'organic', 'sweet', 'whole', 'hot', 'green', 'red', 'gold', 'yellow', 'raw', 'premium', 'vegetable', 'bulbs']
    for j in junk:
        n = re.sub(r'\b' + j + r'\b', '', n)
    
    # Remove specific suffix/prefix logic
    n = re.sub(r'\(.*?\)', '', n) # Remove content in value brackets like (Premium)
    n = n.replace('-', ' ').replace('_', ' ')
    
    # Handle plural
    if n.endswith('oes'): n = n[:-2] # potatoes -> potato, tomatoes -> tomato
    elif n.endswith('s') and not n.endswith('ss') and not n.endswith('us') and not n.endswith('is'): 
        # Very basic check, might be wrong for some, but better than before
        # apples -> apple, noodles -> noodle
        n = n[:-1]
    
    return n.strip()
    
def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch all products
    products = cursor.execute('SELECT product_id, name, image_url, description, price, category_id FROM products').fetchall()
    
    normalized_map = {}
    
    duplicates_found = 0
    missing_images = []
    
    print("--- Checking for Duplicates ---")
    
    for p in products:
        norm = normalize_name(p['name'])
        if not norm: continue # Skip empty names
        
        if norm not in normalized_map:
            normalized_map[norm] = []
        normalized_map[norm].append(p)
        
    # Process duplicates
    for norm_name, prod_list in normalized_map.items():
        if len(prod_list) > 1:
            print(f"Found duplicates for '{norm_name}': {[p['name'] for p in prod_list]}")
            duplicates_found += 1
            
            # Decide which one to keep (shortest name usually best, e.g. "Potato" vs "Fresh Potato")
            # Sort by length of name
            prod_list.sort(key=lambda x: len(x['name']))
            keeper = prod_list[0]
            others = prod_list[1:]
            
            print(f"  -> Keeping: {keeper['name']} (ID: {keeper['product_id']})")
            
            for other in others:
                print(f"  -> Merging: {other['name']} (ID: {other['product_id']})")
                
                # Move images
                other_imgs = conn.execute('SELECT image_id, image_url FROM product_images WHERE product_id = ?', (other['product_id'],)).fetchall()
                for img in other_imgs:
                    # Check if keeper already has this image URL
                    exists = conn.execute('SELECT 1 FROM product_images WHERE product_id = ? AND image_url = ?', (keeper['product_id'], img['image_url'])).fetchone()
                    if not exists:
                         conn.execute('UPDATE product_images SET product_id = ? WHERE image_id = ?', (keeper['product_id'], img['image_id']))
                    else:
                         print(f"    - Skipping duplicate image URL: {img['image_url']}")
                
                # Delete the other product
                conn.execute('DELETE FROM products WHERE product_id = ?', (other['product_id'],))
                
    if duplicates_found == 0:
        print("No duplicates found.")
        
    conn.commit()
    
    # 2. Rename remaining "bad" names (like "Fresh Cabbage" -> "Cabbage") if they are the only ones
    print("\n--- Cleaning remaining names ---")
    products = cursor.execute('SELECT product_id, name FROM products').fetchall() # Re-fetch
    for p in products:
        norm = normalize_name(p['name'])
        # Capitalize
        clean_name = norm.title()
        
        # Helper dictionary for capitalization and fixups
        caps = {
            'Potato': 'Potato', 'Tomato': 'Tomato', 'Okra': 'Okra', 'Paneer': 'Paneer',
            'Noodl': 'Noodles', 'Appl': 'Apple', 'Oat': 'Oats', 'Maggi Noodl': 'Maggi Noodles',
            'Top Ramen': 'Top Ramen', 'Yippee Noodl': 'Yippee Noodles', 'Maggi Oat': 'Maggi Oats'
        }
        if clean_name in caps: clean_name = caps[clean_name]
        
        if clean_name != p['name'] and len(clean_name) > 2:
             # Check if clean name already exists (collision check)
             exists = conn.execute('SELECT 1 FROM products WHERE name = ? AND product_id != ?', (clean_name, p['product_id'])).fetchone()
             if not exists:
                 print(f"Renaming '{p['name']}' -> '{clean_name}'")
                 conn.execute('UPDATE products SET name = ? WHERE product_id = ?', (clean_name, p['product_id']))
             else:
                 print(f"Cannot rename '{p['name']}' -> '{clean_name}' (Target exists)")
                 
    conn.commit()

    # 3. Check for missing images
    print("\n--- Checking for Missing Images ---")
    products = cursor.execute('SELECT product_id, name, image_url FROM products').fetchall()
    
    for p in products:
        has_image = False
        if p['image_url']:
            # Check if file exists
            # Handle potential relative path
            path = p['image_url']
            if path.startswith('/'): path = path.lstrip('/')
            
            if os.path.exists(path):
                has_image = True
            else:
                 print(f"Broken image link for {p['name']}: {p['image_url']}")
                 
        # Also check product_images table if main Image URL is empty
        if not has_image:
             imgs = conn.execute('SELECT image_url FROM product_images WHERE product_id = ?', (p['product_id'],)).fetchall()
             for img in imgs:
                 path = img['image_url']
                 if path.startswith('/'): path = path.lstrip('/')
                 if os.path.exists(path):
                     has_image = True
                     break
        
        if not has_image:
            print(f"MISSING IMAGE: {p['name']}")
            missing_images.append(p['name'])
            
    conn.close()
    
    if missing_images:
        print(f"\nFOUND {len(missing_images)} PRODUCTS WITH MISSING IMAGES.")
        print("Please generate images for:", ", ".join(missing_images))
    else:
        print("\nAll products have valid images.")

if __name__ == '__main__':
    main()
