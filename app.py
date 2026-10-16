"""
Flask Backend for Agriculture/Grocery Application
API Endpoints for all frontend pages
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os
import random
import socket
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('database/agriculture.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and user['password'] == password:  # In production, use password hashing
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'address': user['address']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/login/request-otp', methods=['POST'])
def request_otp():
    """Request OTP for login/signup"""
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    
    if not identifier:
        return jsonify({'success': False, 'message': 'Mobile number required'}), 400
        
    conn = get_db_connection()
    
    # Generate OTP (6 digits)
    otp = str(random.randint(100000, 999999))
    
    # Store OTP in db
    conn.execute('INSERT INTO otps (identifier, otp_code) VALUES (?, ?)', (identifier, otp))
    conn.commit()
    conn.close()
    
    # In a real app, send OTP via SMS or Email here.
    print(f"\n==========================================")
    print(f"OTP for {identifier}: {otp}")
    print(f"==========================================\n")
    
    return jsonify({
        'success': True, 
        'message': 'OTP sent successfully',
        'demo_otp': otp  # For demonstration purposes
    })

@app.route('/api/login/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and login or register"""
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    otp = data.get('otp', '').strip()
    
    if not identifier or not otp:
        return jsonify({'success': False, 'message': 'Identifier and OTP required'}), 400
        
    conn = get_db_connection()
    
    # Verify OTP
    recent_otp = conn.execute('''
        SELECT * FROM otps 
        WHERE identifier = ? AND otp_code = ? 
        ORDER BY created_at DESC LIMIT 1
    ''', (identifier, otp)).fetchone()
    
    if not recent_otp:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 401
        
    # Get User
    user = conn.execute('SELECT * FROM users WHERE email = ? OR phone = ? OR username = ?', (identifier, identifier, identifier)).fetchone()
    
    if not user:
        # User doesn't exist, create automatically
        # Generate a unique username
        base_username = identifier.split('@')[0] if '@' in identifier else f"user_{identifier}"
        username = base_username
        
        # Ensure username uniqueness
        counter = 1
        while conn.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone():
            username = f"{base_username}{counter}"
            counter += 1
            
        email = identifier if '@' in identifier else f"{identifier}@example.com"
        phone = identifier if '@' not in identifier else None
        
        # Insert user
        cursor = conn.execute('''
            INSERT INTO users (username, password, email, phone) 
            VALUES (?, ?, ?, ?)
        ''', (username, 'OTP_LOGIN', email, phone))
        
        # Fetch newly created user
        user = conn.execute('SELECT * FROM users WHERE user_id = ?', (cursor.lastrowid,)).fetchone()
        
    # Delete used OTP
    conn.execute('DELETE FROM otps WHERE identifier = ? AND otp_code = ?', (identifier, otp))
    conn.commit()
    conn.close()
    
    session['user_id'] = user['user_id']
    session['username'] = user['username']
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': {
            'id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'phone': user['phone'],
            'address': user['address']
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        phone = data.get('phone', '').strip() if data.get('phone') else None
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # We auto-generate these since we removed them from the UI to make login sizes perfect
        username = f"user_{phone}" if phone else "user_unknown"
        email = f"{phone}@example.com" if phone else "unknown@example.com"
        address = None
        
        # Validate required fields
        if not phone:
            return jsonify({'success': False, 'message': 'Mobile number is required'}), 400
        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400
        if not confirm_password:
            return jsonify({'success': False, 'message': 'Please confirm your password'}), 400
        
        # Check if passwords match
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
        
        conn = get_db_connection()
        
        try:
            # Create new user
            conn.execute('''
                INSERT INTO users (username, password, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, email, phone, address))
            
            conn.commit()
            user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'user_id': user_id
            })
        except sqlite3.IntegrityError as e:
            conn.close()
            error_msg = str(e)
            if 'UNIQUE constraint failed: users.username' in error_msg:
                return jsonify({'success': False, 'message': 'Username already exists'}), 409
            elif 'UNIQUE constraint failed: users.email' in error_msg:
                return jsonify({'success': False, 'message': 'Email already exists'}), 409
            else:
                return jsonify({'success': False, 'message': 'Database error: ' + error_msg}), 500
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/check-session')
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE user_id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'logged_in': True,
            'user': {
                'id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'address': user['address']
            }
        })
    else:
        return jsonify({'success': True, 'logged_in': False})

# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
        
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        # Add timestamp to make filename unique
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Return the URL
        url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'success': True, 'url': url})
        
    return jsonify({'success': False, 'message': 'Upload failed'}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with pagination and optimization"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    offset = (page - 1) * limit
    
    conn = get_db_connection()
    
    # Get total count
    total_count = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    
    # Optimized query with subqueries for related data and SQL-based priority sorting
    products = conn.execute(f'''
        SELECT p.*, c.name as category_name,
               (SELECT image_url FROM product_images WHERE product_id = p.product_id ORDER BY image_order LIMIT 1) as primary_image,
               (SELECT AVG(rating) FROM product_ratings WHERE product_id = p.product_id) as average_rating,
               (SELECT COUNT(*) FROM product_ratings WHERE product_id = p.product_id) as rating_count
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        ORDER BY 
          CASE 
            WHEN LOWER(p.name) IN ('tomato', 'onion', 'potato', 'milk', 'egg', 'bread', 'rice', 'wheat') THEN 1
            WHEN LOWER(c.name) LIKE '%vegetable%' THEN 2
            WHEN LOWER(c.name) LIKE '%fruit%' THEN 3
            WHEN LOWER(c.name) LIKE '%dairy%' THEN 4
            WHEN LOWER(c.name) LIKE '%grain%' THEN 5
            ELSE 100
          END,
          p.created_at DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset)).fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        p_dict = dict(product)
        # Ensure images array exists for frontend compatibility
        if p_dict.get('primary_image'):
             p_dict['images'] = [p_dict['primary_image']]
        elif p_dict.get('image_url'):
             p_dict['images'] = [p_dict['image_url']]
        else:
             p_dict['images'] = []
        products_list.append(p_dict)
    
    return jsonify({
        'products': products_list,
        'total': total_count,
        'page': page,
        'pages': (total_count + limit - 1) // limit if limit > 0 else 1
    })

@app.route('/api/products/category/<int:category_id>')
def get_products_by_category(category_id):
    """Get products by category with pagination"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    offset = (page - 1) * limit

    conn = get_db_connection()
    
    # Get total count
    total_count = conn.execute('SELECT COUNT(*) FROM products WHERE category_id = ?', (category_id,)).fetchone()[0]

    products = conn.execute('''
        SELECT p.*, c.name as category_name,
               (SELECT image_url FROM product_images WHERE product_id = p.product_id ORDER BY image_order LIMIT 1) as primary_image,
               (SELECT AVG(rating) FROM product_ratings WHERE product_id = p.product_id) as average_rating,
               (SELECT COUNT(*) FROM product_ratings WHERE product_id = p.product_id) as rating_count
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.category_id = ?
        ORDER BY p.created_at DESC
        LIMIT ? OFFSET ?
    ''', (category_id, limit, offset)).fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        p_dict = dict(product)
        if p_dict.get('primary_image'):
             p_dict['images'] = [p_dict['primary_image']]
        elif p_dict.get('image_url'):
             p_dict['images'] = [p_dict['image_url']]
        else:
             p_dict['images'] = []
        products_list.append(p_dict)
    
    return jsonify({
        'products': products_list,
        'total': total_count,
        'page': page,
        'pages': (total_count + limit - 1) // limit if limit > 0 else 1
    })

@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get single product details"""
    conn = get_db_connection()
    product = conn.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = ?
    ''', (product_id,)).fetchone()
    conn.close()
    
    if product:
        product_dict = dict(product)
        
        # Get product images
        conn = get_db_connection()
        images = conn.execute('''
            SELECT image_url FROM product_images 
            WHERE product_id = ? 
            ORDER BY image_order
        ''', (product_id,)).fetchall()
        conn.close()
        product_dict['images'] = [dict(img)['image_url'] for img in images]
        
        # Get average rating and reviews
        conn = get_db_connection()
        rating = conn.execute('''
            SELECT AVG(rating) as avg_rating, COUNT(*) as rating_count
            FROM product_ratings
            WHERE product_id = ?
        ''', (product_id,)).fetchone()
        
        reviews = conn.execute('''
            SELECT pr.*, u.username
            FROM product_ratings pr
            JOIN users u ON pr.user_id = u.user_id
            WHERE pr.product_id = ?
            ORDER BY pr.created_at DESC
        ''', (product_id,)).fetchall()
        conn.close()
        
        product_dict['average_rating'] = rating['avg_rating'] if rating['avg_rating'] else 0
        product_dict['rating_count'] = rating['rating_count'] if rating['rating_count'] else 0
        product_dict['reviews'] = [dict(review) for review in reviews]
        
        return jsonify(product_dict)
    else:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

@app.route('/api/products/search')
def search_products():
    """Search products by name"""
    query = request.args.get('q', '').lower()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    offset = (page - 1) * limit
    
    conn = get_db_connection()
    
    # Get total count
    total_count = conn.execute('''
        SELECT COUNT(*) 
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE LOWER(p.name) LIKE ? OR LOWER(c.name) LIKE ?
    ''', (f'%{query}%', f'%{query}%')).fetchone()[0]

    products = conn.execute('''
        SELECT p.*, c.name as category_name,
               (SELECT image_url FROM product_images WHERE product_id = p.product_id ORDER BY image_order LIMIT 1) as primary_image,
               (SELECT AVG(rating) FROM product_ratings WHERE product_id = p.product_id) as average_rating,
               (SELECT COUNT(*) FROM product_ratings WHERE product_id = p.product_id) as rating_count
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE LOWER(p.name) LIKE ? OR LOWER(c.name) LIKE ?
        ORDER BY p.created_at DESC
        LIMIT ? OFFSET ?
    ''', (f'%{query}%', f'%{query}%', limit, offset)).fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        p_dict = dict(product)
        if p_dict.get('primary_image'):
             p_dict['images'] = [p_dict['primary_image']]
        elif p_dict.get('image_url'):
             p_dict['images'] = [p_dict['image_url']]
        else:
             p_dict['images'] = []
        products_list.append(p_dict)
    
    return jsonify({
        'products': products_list,
        'total': total_count,
        'page': page,
        'pages': (total_count + limit - 1) // limit if limit > 0 else 1
    })

@app.route('/api/products/viewed', methods=['POST'])
def mark_product_viewed():
    """Mark product as viewed by user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID required'}), 400
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO viewed_products (user_id, product_id)
        VALUES (?, ?)
    ''', (session['user_id'], product_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Product marked as viewed'})

@app.route('/api/products/viewed')
def get_viewed_products():
    """Get recently viewed products"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    products = conn.execute('''
        SELECT DISTINCT p.*, c.name as category_name,
               (SELECT image_url FROM product_images WHERE product_id = p.product_id ORDER BY image_order LIMIT 1) as primary_image,
               (SELECT AVG(rating) FROM product_ratings WHERE product_id = p.product_id) as average_rating,
               (SELECT COUNT(*) FROM product_ratings WHERE product_id = p.product_id) as rating_count
        FROM viewed_products vp
        JOIN products p ON vp.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE vp.user_id = ?
        ORDER BY vp.viewed_at DESC
        LIMIT 10
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        p_dict = dict(product)
        if p_dict.get('primary_image'):
             p_dict['images'] = [p_dict['primary_image']]
        elif p_dict.get('image_url'):
             p_dict['images'] = [p_dict['image_url']]
        else:
             p_dict['images'] = []
        products_list.append(p_dict)
    
    return jsonify(products_list)

# ============================================================================
# PRODUCT IMAGES ENDPOINTS
# ============================================================================

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        price = data.get('price')
        category_id = data.get('category_id')
        image_url = data.get('image_url', '').strip()
        stock_quantity = data.get('stock_quantity', 0)
        images = data.get('images', [])  # Array of image URLs
        
        # Validate required fields
        if not name:
            return jsonify({'success': False, 'message': 'Product name is required'}), 400
        if price is None or price <= 0:
            return jsonify({'success': False, 'message': 'Valid price is required'}), 400
        if not category_id:
            return jsonify({'success': False, 'message': 'Category is required'}), 400
        
        conn = get_db_connection()
        
        # Check if category exists
        category = conn.execute('SELECT category_id FROM categories WHERE category_id = ?', (category_id,)).fetchone()
        if not category:
            conn.close()
            return jsonify({'success': False, 'message': 'Category not found'}), 404
        
        # Create product
        cursor = conn.execute('''
            INSERT INTO products (name, description, price, category_id, image_url, stock_quantity, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, price, category_id, image_url, stock_quantity, session['user_id']))
        
        product_id = cursor.lastrowid
        
        # Add images to product_images table
        if images:
            for idx, img_url in enumerate(images):
                if img_url:
                    conn.execute('''
                        INSERT INTO product_images (product_id, image_url, image_order)
                        VALUES (?, ?, ?)
                    ''', (product_id, img_url, idx))
        elif image_url:
            # If single image_url provided, add it to product_images
            conn.execute('''
                INSERT INTO product_images (product_id, image_url, image_order)
                VALUES (?, ?, ?)
            ''', (product_id, image_url, 0))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product_id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating product: {str(e)}'}), 500

@app.route('/api/products/<int:product_id>/images', methods=['POST'])
def add_product_image(product_id):
    """Add image to product"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    image_url = data.get('image_url')
    image_order = data.get('image_order', 0)
    
    if not image_url:
        return jsonify({'success': False, 'message': 'Image URL required'}), 400
    
    conn = get_db_connection()
    
    # Check if product exists
    product = conn.execute('SELECT product_id FROM products WHERE product_id = ?', (product_id,)).fetchone()
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    conn.execute('''
        INSERT INTO product_images (product_id, image_url, image_order)
        VALUES (?, ?, ?)
    ''', (product_id, image_url, image_order))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Image added successfully'})

@app.route('/api/user/products')
def get_user_products():
    """Get products created by the current user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    products = conn.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append(dict(product))
    
    return jsonify(products_list)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    
    # Check if product belongs to user
    product = conn.execute('SELECT user_id FROM products WHERE product_id = ?', (product_id,)).fetchone()
    
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    if product['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Delete product (and cascade delete images/ratings if foreign keys set up, otherwise manual delete)
    # Assuming manual delete for safety if cascade not set
    conn.execute('DELETE FROM product_images WHERE product_id = ?', (product_id,))
    conn.execute('DELETE FROM product_ratings WHERE product_id = ?', (product_id,))
    conn.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Product deleted successfully'})

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    category_id = data.get('category_id')
    image_url = data.get('image_url')
    stock_quantity = data.get('stock_quantity')
    images = data.get('images', None)
    conn = get_db_connection()
    product = conn.execute('SELECT user_id FROM products WHERE product_id = ?', (product_id,)).fetchone()
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    if product['user_id'] != session['user_id']:
        conn.close()
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    conn.execute('''
        UPDATE products
        SET name = COALESCE(?, name),
            description = COALESCE(?, description),
            price = COALESCE(?, price),
            category_id = COALESCE(?, category_id),
            image_url = COALESCE(?, image_url),
            stock_quantity = COALESCE(?, stock_quantity)
        WHERE product_id = ?
    ''', (name, description, price, category_id, image_url, stock_quantity, product_id))
    if isinstance(images, list):
        conn.execute('DELETE FROM product_images WHERE product_id = ?', (product_id,))
        for idx, img in enumerate(images):
            if img:
                conn.execute('''
                    INSERT INTO product_images (product_id, image_url, image_order)
                    VALUES (?, ?, ?)
                ''', (product_id, img, idx))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Product updated successfully'})

# ============================================================================
# PRODUCT RATINGS ENDPOINTS
# ============================================================================

@app.route('/api/products/<int:product_id>/ratings', methods=['POST'])
def add_product_rating(product_id):
    """Add rating to product"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    rating = data.get('rating')
    review = data.get('review', '')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
    
    conn = get_db_connection()
    
    # Check if user already rated this product
    existing_rating = conn.execute('''
        SELECT * FROM product_ratings 
        WHERE product_id = ? AND user_id = ?
    ''', (product_id, session['user_id'])).fetchone()
    
    if existing_rating:
        # Update existing rating
        conn.execute('''
            UPDATE product_ratings
            SET rating = ?, review = ?, created_at = CURRENT_TIMESTAMP
            WHERE product_id = ? AND user_id = ?
        ''', (rating, review, product_id, session['user_id']))
    else:
        # Create new rating
        conn.execute('''
            INSERT INTO product_ratings (product_id, user_id, rating, review)
            VALUES (?, ?, ?, ?)
        ''', (product_id, session['user_id'], rating, review))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Rating submitted successfully'})

# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/analysis/global-prices')
def get_global_prices():
    conn = get_db_connection()
    prices = conn.execute('SELECT * FROM global_crop_prices ORDER BY crop_name, country').fetchall()
    conn.close()
    return jsonify([dict(row) for row in prices])

@app.route('/api/analysis/seasonal-guide')
def get_seasonal_guide():
    conn = get_db_connection()
    # Assuming crops table has season column
    crops = conn.execute('SELECT name, season, description, image_url FROM crops ORDER BY season').fetchall()
    conn.close()
    
    # Group by season
    guide = {}
    for crop in crops:
        season = crop['season']
        if season not in guide:
            guide[season] = []
        guide[season].append(dict(crop))
        
    return jsonify(guide)

@app.route('/api/analysis/fertilizers')
def get_fertilizer_guide():
    conn = get_db_connection()
    # Assuming crops table has fertilizer column
    crops = conn.execute('SELECT name, fertilizer, image_url FROM crops WHERE fertilizer IS NOT NULL').fetchall()
    conn.close()
    return jsonify([dict(row) for row in crops])



@app.route('/api/products/<int:product_id>/ratings')
def get_product_ratings(product_id):
    """Get ratings for product"""
    conn = get_db_connection()
    ratings = conn.execute('''
        SELECT pr.*, u.username
        FROM product_ratings pr
        JOIN users u ON pr.user_id = u.user_id
        WHERE pr.product_id = ?
        ORDER BY pr.created_at DESC
    ''', (product_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(rating) for rating in ratings])

# ============================================================================
# SHOPPING CART ENDPOINTS
# ============================================================================

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get user's shopping cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    cart_items = conn.execute('''
        SELECT ci.*, p.name, p.price, p.image_url, c.name as category_name
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE ci.user_id = ?
        ORDER BY ci.added_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    cart_list = []
    total_amount = 0
    for item in cart_items:
        item_dict = dict(item)
        item_dict['subtotal'] = item['quantity'] * item['price']
        total_amount += item_dict['subtotal']
        cart_list.append(item_dict)
    
    return jsonify({
        'items': cart_list,
        'total_amount': total_amount,
        'item_count': len(cart_list)
    })

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """Add product to cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id or quantity < 1:
        return jsonify({'success': False, 'message': 'Invalid product or quantity'}), 400
    
    conn = get_db_connection()
    
    # Check if product exists
    product = conn.execute('SELECT * FROM products WHERE product_id = ?', (product_id,)).fetchone()
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    # Check if item already in cart
    existing_item = conn.execute('''
        SELECT * FROM cart_items 
        WHERE user_id = ? AND product_id = ?
    ''', (session['user_id'], product_id)).fetchone()
    
    if existing_item:
        # Update quantity
        conn.execute('''
            UPDATE cart_items
            SET quantity = quantity + ?
            WHERE user_id = ? AND product_id = ?
        ''', (quantity, session['user_id'], product_id))
    else:
        # Insert new item
        conn.execute('''
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (?, ?, ?)
        ''', (session['user_id'], product_id, quantity))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Product added to cart'})

@app.route('/api/cart/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    """Update cart item quantity"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    quantity = data.get('quantity')
    
    if not quantity or quantity < 1:
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE cart_items
        SET quantity = ?
        WHERE cart_item_id = ? AND user_id = ?
    ''', (quantity, cart_item_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Cart item updated'})

@app.route('/api/cart/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    conn.execute('''
        DELETE FROM cart_items
        WHERE cart_item_id = ? AND user_id = ?
    ''', (cart_item_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Item removed from cart'})

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    """Clear entire cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    conn.execute('DELETE FROM cart_items WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Cart cleared'})

# ============================================================================
# ORDERS ENDPOINTS
# ============================================================================

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order from cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    shipping_address = data.get('shipping_address')
    shipping_phone = data.get('shipping_phone')
    
    if not shipping_address or not shipping_phone:
        return jsonify({'success': False, 'message': 'Shipping address and phone required'}), 400
    
    conn = get_db_connection()
    
    # Get cart items
    cart_items = conn.execute('''
        SELECT ci.*, p.price
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.product_id
        WHERE ci.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    if not cart_items:
        conn.close()
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400
    
    # Calculate total amount
    total_amount = sum(item['quantity'] * item['price'] for item in cart_items)
    
    # Create order
    cursor = conn.execute('''
        INSERT INTO orders (user_id, total_amount, shipping_address, shipping_phone)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], total_amount, shipping_address, shipping_phone))
    
    order_id = cursor.lastrowid
    
    # Add order items
    for item in cart_items:
        conn.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        ''', (order_id, item['product_id'], item['quantity'], item['price']))
    
    # Clear cart
    conn.execute('DELETE FROM cart_items WHERE user_id = ?', (session['user_id'],))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Order placed successfully',
        'order_id': order_id,
        'total_amount': total_amount
    })

@app.route('/api/orders')
def get_orders_legacy():
    """Get user's orders - Legacy"""
    # This endpoint is deprecated, use /api/user/orders instead
    return get_user_orders()

@app.route('/api/orders/<int:order_id>')
def get_order(order_id):
    """Get order details"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    order = conn.execute('''
        SELECT * FROM orders
        WHERE order_id = ? AND user_id = ?
    ''', (order_id, session['user_id'])).fetchone()
    
    if not order:
        conn.close()
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    order_dict = dict(order)
    
    # Get order items
    order_items = conn.execute('''
        SELECT oi.*, p.name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    order_dict['items'] = [dict(item) for item in order_items]
    conn.close()
    
    return jsonify(order_dict)

# ============================================================================
# NEW FEATURE ENDPOINTS
# ============================================================================

CROPS_DATA = {
    "Cereals": ["Rice", "Wheat", "Maize", "Jowar (Sorghum)", "Bajra (Pearl millet)", "Ragi (Finger millet)", "Foxtail Millet", "Barley", "Oats"],
    "Pulses": ["Gram (Chickpea)", "Tur (Arhar/Pigeon pea)", "Moong (Green gram)", "Urad (Black gram)", "Masur (Lentil)", "Peas", "Kidney Beans", "Cowpea", "Adzuki Bean"],
    "Oilseeds": ["Groundnut", "Mustard", "Soybean", "Sunflower", "Sesame (Til)", "Linseed", "Castor"],
    "Cash Crops": ["Cotton", "Sugarcane", "Jute", "Tea", "Coffee", "Rubber", "Tobacco", "Arecanut", "Sindoor"],
    "Fruits": ["Mango", "Banana", "Apple", "Orange", "Grapes", "Papaya", "Pineapple", "Bael", "Guava", "Jackfruit", "Lychee", "Rose Apple", "Watermelon", "Lemon", "Muskmelon"],
    "Dry Fruits": ["Almond", "Walnut"],
    "Vegetables": ["Potato", "Tomato", "Onion", "Brinjal (Eggplant)", "Cabbage", "Cauliflower", "Bottle Gourd", "Cucumber", "Pumpkins", "Vegetables"],
    "Spices": ["Turmeric", "Ginger", "Black Pepper", "Cardamom", "Clove", "Cinnamon", "Coriander", "Cumin", "Fenugreek", "Garlic"]
}

@app.route('/api/all-crops')
def get_all_crops_list():
    # Helper to clean crop names for matching (e.g. "Gram (Chickpea)" -> "Gram")
    def clean_name(name):
        return name.split('(')[0].strip().lower()

    # Get images from DB
    conn = get_db_connection()
    # Get distinct product names and their images
    db_products = conn.execute('SELECT name, image_url FROM products GROUP BY name').fetchall()
    conn.close()
    
    # Create mapping
    image_map = {}
    for p in db_products:
        image_map[p['name'].lower()] = p['image_url']
        # Also map partials? e.g. "Sweet Corn" -> "Corn" - maybe too risky.
        # But we can map "Sweet Corn" to "Sweet Corn".
        
    # Also add some manual mappings/fallbacks based on what we know exists
    # This helps bridge the gap between CROPS_DATA names and Product names
    # Updated manual mappings to use images from 'Market Prices' directory
    # Updated manual mappings with FULL PATHS to distinguish between folders
    manual_map = {
        # --- FROM MARKET PRICES (Preferred) ---
        "rice": "/static/images/Market Prices/rice_paddy.jpg",
        "wheat": "/static/images/Market Prices/wheat_field.jpg",
        "foxtail millet": "/static/images/Market Prices/Japanese_Foxtail_millet_02.jpg",
        "black gram": "/static/images/Market Prices/Black_gram.jpg",
        "urad (black gram)": "/static/images/Market Prices/Black_gram.jpg",
        "pigeon pea": "/static/images/Market Prices/Pigeon_Pea.jpeg",
        "tur (arhar/pigeon pea)": "/static/images/Market Prices/Pigeon_Pea.jpeg",
        "kidney beans": "/static/images/Market Prices/489idea99Red-kidney-beans-2.jpg",
        "cowpea": "/static/images/Market Prices/2023-0801-0057+Conley+cowpea-save4web.jpg.webp",
        "adzuki bean": "/static/images/Market Prices/Vigna-unguiculata-Adzuki-bean-plant.jpg",
        "red lentil": "/static/images/Market Prices/stock-photo-close-view-uncooked-red-lentil-seeds.jpeg",
        "masur (lentil)": "/static/images/Market Prices/stock-photo-close-view-uncooked-red-lentil-seeds.jpeg",
        "mustard": "/static/images/Market Prices/mustard-plant.jpg",
        "mustard seeds": "/static/images/Market Prices/SK_SpiceShop_MustardSeeds-small.jpg",
        "black pepper": "/static/images/Market Prices/black_pepper.jpg",
        "coriander": "/static/images/products/coriander.png",
        "garlic": "/static/images/Market Prices/garlic.jpg",
        "turmeric": "/static/images/Market Prices/turmeric.jpg",
        "sugarcane": "/static/images/Market Prices/689FFBA0-D431-4D9A-8BFB1805602316FC-sugarcane-with-driperline.jpg",
        "arecanut": "/static/images/Market Prices/arecanut.jpg",
        "orange": "/static/images/Market Prices/orange-tree-nature-fruit.jpg",
        "papaya": "/static/images/Market Prices/papaya.jpg",
        "watermelon": "/static/images/Market Prices/watermelon.jpg",
        "muskmelon": "/static/images/products/muskmelon.png",
        "bael": "/static/images/Market Prices/1708421453-how-to-do-bael-cultivation-completed-information.jpg",
        "guava": "/static/images/Market Prices/guava-fruit-4k-footage-guavas-footage-296338344_iconl.jpeg",
        "jackfruit": "/static/images/Market Prices/jackfruit-green-fruit-delicious-food-exotic-royalty-free-thumbnail.jpg",
        "lychee": "/static/images/Market Prices/grow-lychee-inside-1902624-hero-c9295040c0dd4af4b9c582d629f92e1e.jpg",
        "rose apple": "/static/images/Market Prices/syzygium-jambos-tree-rose-apple-fruit.jpg",
        "almond": "/static/images/Market Prices/almendro01.jpg",
        "walnut": "/static/images/Market Prices/walnut-tree-fruit-1024x672.jpg",
        "tomato": "/static/images/Market Prices/how_to_grow_tomatoes.jpg",
        "bottle gourd": "/static/images/Market Prices/bottle_gourd.jpg",
        "cucumber": "/static/images/products/cucumber.png",
        "vegetables": "/static/images/products/vegetables_mix.png",
        "sindoor": "/static/images/Market Prices/sindoor-plant.jpeg",
        "sesame (til)": "/static/images/Market Prices/sesame.jpg",
        "soybean": "/static/images/Market Prices/soybean.jpg",
        "cinnamon": "/static/images/Market Prices/cinnamon-removebg-preview.png",
        "clove": "/static/images/Market Prices/clove-removebg-preview.png",
        "cumin": "/static/images/Market Prices/cumin-removebg-preview.png",
        "fenugreek": "/static/images/Market Prices/fenugreek.jpg",
        "cardamom": "/static/images/Market Prices/cardamom-removebg-preview.png",
        "coffee": "/static/images/Market Prices/coffee_plantation.jpg",
        "tea": "/static/images/products/tea_field.png",
        "rubber": "/static/images/products/rubber_tree.png",
        "linseed": "/static/images/Market Prices/sesame.jpg",
        "castor": "/static/images/Market Prices/peanut_plant.jpg",
        
        # --- MAPPED REMAINING IMAGES ---
        "groundnut": "/static/images/Market Prices/peanut_plant.jpg",
        "bajra (pearl millet)": "/static/images/Market Prices/1740470977371.png",
        "jowar (sorghum)": "/static/images/Market Prices/1751449262_2aa231a23ef880a46c90.png",
        "sunflower": "/static/images/Market Prices/sunflower_field.jpg",
        "cotton": "/static/images/Market Prices/cotton_field.jpg",
        "gram (chickpea)": "/static/images/Market Prices/chickpea-removebg-preview.png",
        "moong (green gram)": "/static/images/products/6f04b8b1f692bb7788a53a8512a5e141-removebg-preview.png",
        "lemon": "/static/images/Market Prices/photo-1597714026720-8f74c62310ba.jpeg",
        "tobacco": "/static/images/Market Prices/Untitled-1-99-768x427.jpg",
        "jute": "/static/images/Market Prices/P608040-1_1.png",
        "ragi (finger millet)": "/static/images/Market Prices/1740470977371.png",
        # --- FROM PRODUCTS (Legacy/Fallback) ---
        "maize": "/static/images/Market Prices/corn_field.jpg",
        "potato": "/static/images/products/potato_image_1.png",
        "onion": "/static/images/products/onion_image_1.png",
        "carrot": "/static/images/products/carrot_image.png",
        "cabbage": "/static/images/products/34ef49aa5a42066812f2c42d0c2e8a63-removebg-preview.png",
        "cauliflower": "/static/images/products/_Pngtree_vegetable_cauliflower_14914479-removebg-preview.png",
        "brinjal (eggplant)": "/static/images/products/72a4848a9927a857c4d90fdbf93015c2-removebg-preview.png",
        "green peas": "/static/images/products/6f04b8b1f692bb7788a53a8512a5e141-removebg-preview.png",
        "peas": "/static/images/products/6f04b8b1f692bb7788a53a8512a5e141-removebg-preview.png",
        "ginger": "/static/images/products/c6be5acf79f2b357eabc977387246ace-removebg-preview.png",
        "banana": "/static/images/products/banana_image_1.png",
        "apple": "/static/images/products/apple_image.png",
        "grapes": "/static/images/products/grapes_image_1.png",
        "mango": "/static/images/products/mango_image_1.png",
        "spinach": "/static/images/products/spinach_image_1.png",
        "corn": "/static/images/Market Prices/corn_field.jpg",
        "pumpkin": "/static/images/products/isolated-fresh-orange-pumpkin-with-green-leaves-removebg-preview.png",
        "pumpkins": "/static/images/products/isolated-fresh-orange-pumpkin-with-green-leaves-removebg-preview.png",
        "avocado": "/static/images/products/pngimg.com_-_avocado_PNG15510-removebg-preview.png",
        
        # --- NEW MISSING MAPPINGS ---
        "barley": "/static/images/Market Prices/barley.jpg",
        "oats": "/static/images/Market Prices/oats_field.webp"
    }
    
    # Process CROPS_DATA to include images
    enriched_data = {}
    for category, crops in CROPS_DATA.items():
        enriched_data[category] = []
        for crop in crops:
            image_url = ''
            
            # 1. Try manual map (exact) - Prioritize curated images
            if crop.lower() in manual_map:
                image_url = manual_map[crop.lower()]
                
            # 2. Try legacy format in manual map
            elif clean_name(crop) in manual_map:
                image_url = manual_map[clean_name(crop)]

            # 3. Try exact match in DB
            elif crop.lower() in image_map:
                image_url = image_map[crop.lower()]
                
            # 4. Try cleaned name in DB
            elif clean_name(crop) in image_map:
                image_url = image_map[clean_name(crop)]
            
            # Default category fallbacks if still empty
            if not image_url:
                category_fallbacks = {
                    "Cereals": "/static/images/Market Prices/wheat_field.jpg",
                    "Pulses": "/static/images/Market Prices/Pigeon_Pea.jpeg",
                    "Oilseeds": "/static/images/Market Prices/mustard-plant.jpg",
                    "Cash Crops": "/static/images/Market Prices/cotton_field.jpg",
                    "Fruits": "/static/images/products/apple_image.png",
                    "Dry Fruits": "/static/images/Market Prices/almendro01.jpg",
                    "Vegetables": "/static/images/products/tomato_image.png",
                    "Spices": "/static/images/Market Prices/black_pepper.jpg"
                }
                image_url = category_fallbacks.get(category, '/static/images/products/potato_image_1.png')
                 
            enriched_data[category].append({
                'name': crop,
                'image': image_url
            })

    # Return structured data if requested, else flat list
    if request.args.get('structured') == 'true':
        return jsonify(enriched_data)
    
    # Flatten list for backward compatibility
    flat_list = []
    for category in enriched_data.values():
        for crop_obj in category:
            flat_list.append(crop_obj['name'])
    return jsonify(sorted(flat_list))

@app.route('/api/recommend-crop', methods=['POST'])
def recommend_crop():
    data = request.get_json()
    soil_type = data.get('soil_type', '')
    # Handle both string/number inputs safely
    try:
        rainfall = float(data.get('rainfall', 0))
    except (ValueError, TypeError):
        rainfall = 0
        
    try:
        temperature = float(data.get('temperature', 0))
    except (ValueError, TypeError):
        temperature = 0
        
    season = data.get('season', '').lower()

    # Define crop sets for Soil Types
    soil_crops = set()
    if soil_type == "Clay":
        soil_crops.update(["Rice", "Sugarcane", "Soybean", "Wheat", "Gram (Chickpea)", "Jute"])
    elif soil_type == "Sandy":
        soil_crops.update(["Bajra (Pearl millet)", "Groundnut", "Potato", "Watermelon", "Muskmelon", "Maize", "Barley"])
    elif soil_type == "Black":
        soil_crops.update(["Cotton", "Soybean", "Jowar (Sorghum)", "Wheat", "Gram (Chickpea)", "Orange", "Sugarcane", "Sunflower"])
    elif soil_type == "Loamy":
        soil_crops.update(["Wheat", "Maize", "Mustard", "Sugarcane", "Cotton", "Rice", "Tur (Arhar/Pigeon pea)", "Vegetables", "Fruits"])
    elif soil_type == "Red":
        soil_crops.update(["Groundnut", "Ragi (Finger millet)", "Tobacco", "Potato", "Mango", "Rice", "Jowar (Sorghum)"])

    # Define crop sets for Seasons
    season_crops = set()
    if season in ["kharif", "rainy", "monsoon"]: # Warm, Wet (June-Oct)
         season_crops.update(["Rice", "Maize", "Cotton", "Groundnut", "Soybean", "Tur (Arhar/Pigeon pea)", "Bajra (Pearl millet)", "Sugarcane", "Jowar (Sorghum)", "Jute", "Moong (Green gram)"])
    elif season in ["rabi", "winter"]: # Cool, Dry (Oct-March)
         season_crops.update(["Wheat", "Gram (Chickpea)", "Mustard", "Peas", "Potato", "Tomato", "Oats", "Barley", "Sunflower", "Linseed"])
    elif season in ["zaid", "summer"]: # Hot, Dry (March-June)
         season_crops.update(["Watermelon", "Cucumber", "Muskmelon", "Moong (Green gram)", "Sunflower", "Groundnut", "Pumpkins", "Vegetables"])

    # Intersection Logic: Values must satisfy BOTH Soil and Season if both are provided
    recommendations = set()
    
    if soil_crops and season_crops:
        recommendations = soil_crops.intersection(season_crops)
        # If intersection is too strict and returns nothing, fallback to weighted preference (Season > Soil)
        if not recommendations:
             recommendations = season_crops
    elif season_crops:
        recommendations = season_crops
    elif soil_crops:
        recommendations = soil_crops
    else:
        # Default fallback if nothing selected
        recommendations = {"Wheat", "Rice", "Maize"}

    # Weather-based Adjustments (Refinement)
    
    # High Temperature (> 35°C): Avoid cool season crops
    if temperature > 35:
        recommendations.discard("Wheat")
        recommendations.discard("Potato")
        recommendations.discard("Mustard")
        recommendations.discard("Peas")
        recommendations.discard("Gram (Chickpea)")
    
    # Low Temperature (< 15°C): Avoid warm season crops
    if temperature > 0 and temperature < 15:
        recommendations.discard("Rice")
        recommendations.discard("Cotton")
        recommendations.discard("Sugarcane")
        recommendations.discard("Maize")

    # High Rainfall (> 200mm): Suggest water-loving crops
    if rainfall > 200:
        if "Rice" not in recommendations and soil_type != "Sandy": 
            recommendations.add("Rice")
        if "Sugarcane" not in recommendations and soil_type != "Sandy":
            recommendations.add("Sugarcane")
            
    # Low Rainfall (< 50mm): Ensure drought-tolerant crops are present if season permits
    if rainfall > 0 and rainfall < 50:
        if "Bajra (Pearl millet)" in season_crops: recommendations.add("Bajra (Pearl millet)")
        if "Jowar (Sorghum)" in season_crops: recommendations.add("Jowar (Sorghum)")

    # Flatten master list for validation/filtering
    all_crops_flat = []
    for category, crop_list in CROPS_DATA.items():
        all_crops_flat.extend(crop_list)
        # Add basic vegetables key if used
        if category == "Vegetables":
             all_crops_flat.append("Vegetables")

    # Filter to only return known crops (Optional, but good for consistency)
    final_recs = list(recommendations)
    
    # Sort for consistency
    final_recs.sort()
    
    return jsonify({'recommendations': final_recs[:8]}) # Return up to 8 recs

@app.route('/api/predict-price', methods=['POST'])
def predict_price():
    data = request.get_json()
    crop = data.get('crop')
    days = int(data.get('days', 0))
    
    # Mock Logic with Realistic Base Prices (Per Quintal i.e., 100kg)
    # Based on approximate market rates in India (2025-26)
    base_prices_map = {
        'Almond': 85000, 'Arecanut': 62000, 'Black Pepper': 54000, 'Walnut': 92000,
        'Tea': 32000, 'Tobacco': 21000, 'Garlic': 16000, 'Kidney Beans': 13000,
        'Turmeric': 12500, 'Pigeon Pea': 11500, 'Groundnut': 10500, 'Rose Apple': 11000,
        'Lychee': 10000, 'Black Gram': 9500, 'Red Lentil': 9200, 'Adzuki Bean': 9000,
        'Cowpea': 8500, 'Lemon': 8000, 'Gram (Chickpea)': 7500, 'Mustard Seeds': 7200,
        'Cotton': 6500, 'Sunflower': 6200, 'Orange': 6000, 'Guava': 5500,
        'Rice': 5200, 'Jute': 4800, 'Foxtail Millet': 4500, 'Papaya': 4200, 'Jackfruit': 4000,
        'Bael': 3800, 'Jowar (Sorghum)': 3600, 'Wheat': 3200, 'Tomato': 3000,
        'Bajra (Pearl Millet)': 2600, 'Watermelon': 2500, 'Bottle Gourd': 2200,
        'Sugarcane': 1500
    }
    
    # Get base price for crop, default to 3000 if not found
    base_price = base_prices_map.get(crop, 3000)
    
    # Add slight random variation to simulated time-based prediction
    # but keep it close to the base price to be realistic
    base_price = base_price * (random.uniform(0.95, 1.05))
    import random
    
    predicted_prices = []
    current_date = datetime.now()
    
    for i in range(1, days + 1):
        fluctuation = random.uniform(-50, 50)
        price = base_price + (i * 10) + fluctuation
        predicted_prices.append({
            'day': i,
            'price': round(price, 2)
        })
        
    return jsonify({
        'crop': crop,
        'predictions': predicted_prices,
        'final_price': predicted_prices[-1]['price']
    })

@app.route('/api/recommend-fertilizer', methods=['POST'])
def recommend_fertilizer():
    data = request.get_json()
    crop = data.get('crop')
    area = float(data.get('area', 0))
    
    # Mock Logic
    # NPK per acre (mock values)
    npk_map = {
        "Rice": {"N": 40, "P": 20, "K": 20},
        "Wheat": {"N": 50, "P": 25, "K": 25},
        # Default
        "default": {"N": 30, "P": 30, "K": 30}
    }
    
    reqs = npk_map.get(crop, npk_map["default"])
    
    total_n = reqs["N"] * area
    total_p = reqs["P"] * area
    total_k = reqs["K"] * area
    
    recommendations = [
        {"name": "Urea", "amount": f"{round(total_n * 2.2, 1)} kg"}, # Urea is 46% N
        {"name": "DAP", "amount": f"{round(total_p * 2.2, 1)} kg"}, # DAP is 46% P
        {"name": "MOP", "amount": f"{round(total_k * 1.7, 1)} kg"}  # MOP is 60% K
    ]
    
    return jsonify({
        'crop': crop,
        'npk_requirements': reqs,
        'recommendations': recommendations
    })

@app.route('/api/estimate-cost', methods=['POST'])
def estimate_cost():
    data = request.get_json()
    crop = data.get('crop')
    area = float(data.get('area', 0))
    
    # Mock Logic: Cost per acre
    base_cost_per_acre = 15000 
    
    if crop in ["Rice", "Wheat"]:
        base_cost_per_acre = 20000
    elif crop in ["Cotton", "Sugarcane"]:
        base_cost_per_acre = 25000
        
    total_cost = base_cost_per_acre * area
    
    # Breakdown
    breakdown = {
        "Seeds": round(total_cost * 0.15, 2),
        "Fertilizers": round(total_cost * 0.20, 2),
        "Pesticides": round(total_cost * 0.10, 2),
        "Land Preparation": round(total_cost * 0.15, 2),
        "Irrigation": round(total_cost * 0.10, 2),
        "Labor": round(total_cost * 0.20, 2),
        "Harvesting": round(total_cost * 0.05, 2),
        "Miscellaneous": round(total_cost * 0.05, 2)
    }
    
    return jsonify({
        'crop': crop,
        'area': area,
        'total_cost': total_cost,
        'breakdown': breakdown
    })

# ============================================================================
# CATEGORY ENDPOINTS
# ============================================================================

@app.route('/api/categories')
def get_categories():
    """Get all categories"""
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    
    return jsonify([dict(category) for category in categories])

# ============================================================================
# CROP ENDPOINTS
# ============================================================================

@app.route('/api/crops')
def get_crops():
    """Get all crops"""
    conn = get_db_connection()
    crops = conn.execute('SELECT * FROM crops ORDER BY name').fetchall()
    conn.close()
    
    return jsonify([dict(crop) for crop in crops])

@app.route('/api/crops/season/<season>')
def get_crops_by_season(season):
    """Get crops by season"""
    conn = get_db_connection()
    crops = conn.execute('SELECT * FROM crops WHERE LOWER(season) = LOWER(?) ORDER BY name', (season,)).fetchall()
    conn.close()
    
    return jsonify([dict(crop) for crop in crops])

# ============================================================================
# GROWTH DATA ENDPOINTS
# ============================================================================

@app.route('/api/growth-data')
def get_growth_data():
    """Get all growth data"""
    conn = get_db_connection()
    growth_data = conn.execute('''
        SELECT gd.*, c.name as crop_name
        FROM growth_data gd
        JOIN crops c ON gd.crop_id = c.crop_id
        ORDER BY gd.crop_id, gd.year
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(data) for data in growth_data])

@app.route('/api/growth-data/crop/<int:crop_id>')
def get_growth_data_by_crop(crop_id):
    """Get growth data for specific crop"""
    conn = get_db_connection()
    growth_data = conn.execute('''
        SELECT gd.*, c.name as crop_name
        FROM growth_data gd
        JOIN crops c ON gd.crop_id = c.crop_id
        WHERE gd.crop_id = ?
        ORDER BY gd.year
    ''', (crop_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(data) for data in growth_data])

# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@app.route('/api/profile')
def get_profile():
    """Get current user profile"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return jsonify(dict(user))

@app.route('/api/user/profile')
def get_user_profile_data():
    """Get current user profile"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    user = conn.execute('SELECT user_id, username, email, phone, address FROM users WHERE user_id = ?', (session['user_id'],)).fetchone()
    
    # Mock wallet balance (random for demo)
    wallet_balance = 0
    if user:
         wallet_balance = 1500.00 # Demo value
         
    conn.close()
    
    if user:
        user_dict = dict(user)
        user_dict['wallet_balance'] = wallet_balance
        return jsonify(user_dict)
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/api/user/orders')
def get_user_orders():
    """Get user orders with items"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    orders_list = []
    for order in orders:
        o_dict = dict(order)
        # Get items for this order
        items = conn.execute('''
            SELECT oi.*, p.name as product_name, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        ''', (order['order_id'],)).fetchall()
        
        o_dict['items'] = [dict(item) for item in items]
        orders_list.append(o_dict)
        
    conn.close()
    return jsonify(orders_list)

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    """Update user profile"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    
    conn = get_db_connection()
    
    # Update user information
    try:
        if name:
            conn.execute('''
                UPDATE users
                SET username = COALESCE(?, username),
                    email = COALESCE(?, email),
                    phone = COALESCE(?, phone),
                    address = COALESCE(?, address)
                WHERE user_id = ?
            ''', (name, email, phone, address, session['user_id']))
        else:
            conn.execute('''
                UPDATE users
                SET email = COALESCE(?, email),
                    phone = COALESCE(?, phone),
                    address = COALESCE(?, address)
                WHERE user_id = ?
            ''', (email, phone, address, session['user_id']))
            
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        error_msg = str(e)
        if 'username' in error_msg.lower():
            return jsonify({'success': False, 'message': 'Username already exists.'}), 400
        elif 'email' in error_msg.lower():
            return jsonify({'success': False, 'message': 'Email already exists.'}), 400
        else:
            return jsonify({'success': False, 'message': 'Details already exist.'}), 400
    finally:
        conn.close()
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main application"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Serve login page"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Serve registration page (now merged with login)"""
    return redirect(url_for('login_page'))

@app.route('/select-language')
def select_language_page():
    """Serve the dedicated language selection page after login"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('select_language.html')

@app.route('/product/<int:product_id>')
def product_page(product_id):
    """Serve product detail page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('product.html', product_id=product_id)

@app.route('/cart')
def cart_page():
    """Serve cart page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('cart.html')

@app.route('/checkout')
def checkout_page():
    """Serve checkout page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('checkout.html')

def is_port_available(port):
    """Check if a port is available by trying to bind to it"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    data = request.get_json()
    crop = data.get('crop')
    area = float(data.get('area', 0))
    
    # Mock Cost Logic (per acre)
    # These are illustrative values
    base_costs = {
        "Seeds": 1500,
        "Fertilizers": 3500,
        "Pesticides": 2000,
        "Land Preparation": 4000,
        "Labor": 8000,
        "Irrigation": 2500,
        "Harvesting": 5000,
        "Miscellaneous": 1000
    }
    
    # Adjust slightly based on crop type (mock)
    if crop in ["Cotton", "Sugarcane"]:
        multiplier = 1.5
    elif crop in ["Rice", "Wheat"]:
        multiplier = 1.0
    else:
        multiplier = 0.8
        
    cost_breakdown = {}
    total_amount = 0
    
    for category, cost in base_costs.items():
        # Calculate specific cost
        final_cost = cost * area * multiplier
        cost_breakdown[category] = round(final_cost, 2)
        total_amount += final_cost
        
    return jsonify({
        'crop': crop,
        'area': area,
        'breakdown': cost_breakdown,
        'total_amount': round(total_amount, 2)
    })

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def create_database():
    """Create the SQLite3 database and all tables"""
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('database/agriculture.db')
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Categories Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category_id INTEGER NOT NULL,
            user_id INTEGER,
            image_url TEXT,
            stock_quantity INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # 4. Product Images Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_images (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            image_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )
    ''')
    
    # 5. Crops Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            season TEXT NOT NULL,
            fertilizer TEXT,
            description TEXT,
            growth_period TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 6. Growth Data Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS growth_data (
            growth_id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            yield_amount REAL,
            growth_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (crop_id) REFERENCES crops(crop_id)
        )
    ''')
    
    # 7. User Products Viewed Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS viewed_products (
            view_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # 8. Shopping Cart Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # 9. Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            shipping_address TEXT NOT NULL,
            shipping_phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # 10. Order Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # 11. Product Ratings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_ratings (
            rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating REAL NOT NULL,
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # 12. Global Crop Prices Table (New)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_crop_prices (
            price_id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            country TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT NOT NULL,
            date DATE DEFAULT CURRENT_DATE
        )
    ''')
    
    # --- ADDED INDEXES FOR PERFORMANCE ---
    print("Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_user ON products(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_images_product ON product_images(product_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_ratings_product ON product_ratings(product_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_viewed_products_user ON viewed_products(user_id)')


    try:
        cols = cursor.execute('PRAGMA table_info(products)').fetchall()
        if not any(col[1] == 'user_id' for col in cols):
            cursor.execute('ALTER TABLE products ADD COLUMN user_id INTEGER')
    except Exception:
        pass

    conn.commit()
    conn.close()
    print("Database tables created successfully.")

def init_database():
    """Initialize the database with sample data"""
    # Check if data already exists to avoid duplicates
    conn = sqlite3.connect('database/agriculture.db')
    cursor = conn.cursor()
    
    # Check categories
    cursor.execute('SELECT count(*) FROM categories')
    if cursor.fetchone()[0] > 0:
        conn.close()
        print("Database already initialized with data.")
        return

    print("Populating database with sample data...")
    
    # --- 1. Categories ---
    categories = [
        ('Vegetables', 'Freshly harvested vegetables', '/static/images/categories/vegetables.jpg'),
        ('Fruits', 'Seasonal and exotic fruits', '/static/images/categories/fruits.jpg'),
        ('Grains', 'Staple grains and pulses', '/static/images/categories/grains.jpg'),
        ('Dairy', 'Milk, cheese, and other dairy products', '/static/images/categories/dairy.jpg'),
    ]
    
    for name, desc, img in categories:
        cursor.execute('INSERT INTO categories (name, description, image_url) VALUES (?, ?, ?)', (name, desc, img))
    
    conn.commit()
    
    # Get category IDs
    vegetables_id = cursor.execute("SELECT category_id FROM categories WHERE name='Vegetables'").fetchone()[0]
    fruits_id = cursor.execute("SELECT category_id FROM categories WHERE name='Fruits'").fetchone()[0]
    grains_id = cursor.execute("SELECT category_id FROM categories WHERE name='Grains'").fetchone()[0]
    dairy_id = cursor.execute("SELECT category_id FROM categories WHERE name='Dairy'").fetchone()[0]
    
    # --- 2. Products ---
    products = [
        # Vegetables
        ('Fresh Tomatoes', 'Juicy, red tomatoes perfect for salads and cooking.', 2.50, vegetables_id, '/static/images/products/tomato.jpg', 150),
        ('Organic Potatoes', 'High-quality organic potatoes, great for mashing or frying.', 1.80, vegetables_id, '/static/images/products/potato.jpg', 200),
        ('Red Onions', 'Sharp and flavorful red onions.', 1.20, vegetables_id, '/static/images/products/onion.jpg', 180),
        ('Sweet Carrots', 'Crisp and sweet carrots.', 0.90, vegetables_id, '/static/images/products/carrot.jpg', 250),
        ('Bell Pepper', 'Sweet and crunchy bell peppers.', 3.00, vegetables_id, '/static/images/products/vegetables_mix.jpg', 120),
        ('Broccoli', 'Fresh green broccoli heads.', 2.20, vegetables_id, '/static/images/products/mixed_greens.jpg', 100),
        
        # Grains
        ('Wheat Grain', 'Premium quality wheat grain.', 0.50, grains_id, '/static/images/products/wheat.jpg', 500),
        ('Basmati Rice', 'Aromatic long-grain basmati rice.', 1.50, grains_id, '/static/images/products/rice.jpg', 400),
        ('Whole Wheat Bread', 'Freshly baked whole wheat bread.', 2.80, grains_id, '/static/images/products/dairy_bread.jpg', 90),
        
        # Fruits
        ('Bananas', 'Ripe yellow bananas.', 0.80, fruits_id, '/static/images/products/banana_grapes.jpg', 300),
        ('Grapes', 'Sweet red and green grapes.', 4.50, fruits_id, '/static/images/products/fruit_basket.jpg', 150),
        
        # Dairy
        ('Fresh Milk', 'Pasteurized fresh cow\'s milk.', 3.50, dairy_id, '/static/images/products/dairy_bread.jpg', 80),
        ('Cheddar Cheese', 'Block of aged cheddar cheese.', 6.00, dairy_id, '/static/images/products/cheese_eggs.jpg', 50),
    ]
    
    for name, desc, price, cat_id, img, stock in products:
        cursor.execute('INSERT INTO products (name, description, price, category_id, image_url, stock_quantity) VALUES (?, ?, ?, ?, ?, ?)', 
                       (name, desc, price, cat_id, img, stock))
    
    conn.commit()
    
    # Get product IDs
    product_ids = {name: cursor.execute("SELECT product_id FROM products WHERE name=?", (name,)).fetchone()[0] for name, _, _, _, _, _ in products}
    
    # --- 3. Product Images ---
    for name, id in product_ids.items():
        img_url = cursor.execute("SELECT image_url FROM products WHERE product_id=?", (id,)).fetchone()[0]
        cursor.execute('INSERT INTO product_images (product_id, image_url, image_order) VALUES (?, ?, ?)', (id, img_url, 0))

    conn.commit()

    # --- 4. Users ---
    cursor.execute('INSERT INTO users (username, password, email, phone, address) VALUES (?, ?, ?, ?, ?)', 
                   ('testuser', 'password', 'test@example.com', '1234567890', '123 Farm Road, Green City'))
    conn.commit()
    test_user_id = cursor.execute("SELECT user_id FROM users WHERE username='testuser'").fetchone()[0]

    # --- 5. Product Ratings ---
    for product_id in product_ids.values():
        num_ratings = random.randint(5, 20)
        for _ in range(num_ratings):
            rating = random.choice([3.0, 3.5, 4.0, 4.5, 5.0])
            review = random.choice([
                'Excellent product, very fresh!',
                'Good quality, but a bit pricey.',
                'Highly recommend this item.',
                'Average, nothing special.',
                'The best I have ever bought.',
                None
            ])
            cursor.execute('INSERT INTO product_ratings (product_id, user_id, rating, review) VALUES (?, ?, ?, ?)', 
                           (product_id, test_user_id, rating, review))
    
    conn.commit()

    # --- 6. Crops ---
    crops = [
        ('Maize', 'Summer', 'Urea, DAP', 'A staple crop grown widely.', '90 days', 'https://via.placeholder.com/300x200?text=Maize'),
        ('Rice', 'Monsoon', 'NPK', 'Requires heavy rainfall.', '120 days', 'https://via.placeholder.com/300x200?text=Rice'),
        ('Wheat', 'Winter', 'Potash', 'Grown in cooler climates.', '150 days', 'https://via.placeholder.com/300x200?text=Wheat'),
    ]
    
    for name, season, fert, desc, period, img in crops:
        cursor.execute('INSERT INTO crops (name, season, fertilizer, description, growth_period, image_url) VALUES (?, ?, ?, ?, ?, ?)', 
                       (name, season, fert, desc, period, img))
    
    conn.commit()
    
    # Get crop IDs
    crop_ids = {name: cursor.execute("SELECT crop_id FROM crops WHERE name=?", (name,)).fetchone()[0] for name, _, _, _, _, _ in crops}
    
    # --- 7. Growth Data ---
    # Sample growth data for Maize
    maize_id = crop_ids['Maize']
    maize_data = [
        (2020, 100, 5.0), (2021, 105, 5.0), (2022, 115, 9.5), (2023, 120, 4.3), (2024, 135, 12.5)
    ]
    for year, yield_amount, growth_rate in maize_data:
        cursor.execute('INSERT INTO growth_data (crop_id, year, yield_amount, growth_rate) VALUES (?, ?, ?, ?)', 
                       (maize_id, year, yield_amount, growth_rate))

    # Sample growth data for Rice
    rice_id = crop_ids['Rice']
    rice_data = [
        (2020, 200, 3.0), (2021, 210, 5.0), (2022, 205, -2.4), (2023, 220, 7.3), (2024, 230, 4.5)
    ]
    for year, yield_amount, growth_rate in rice_data:
        cursor.execute('INSERT INTO growth_data (crop_id, year, yield_amount, growth_rate) VALUES (?, ?, ?, ?)', 
                       (rice_id, year, yield_amount, growth_rate))

    # Sample growth data for Wheat
    wheat_id = crop_ids['Wheat']
    wheat_data = [
        (2020, 150, 4.0), (2021, 160, 6.7), (2022, 170, 6.2), (2023, 165, -2.9), (2024, 180, 9.1)
    ]
    for year, yield_amount, growth_rate in wheat_data:
        cursor.execute('INSERT INTO growth_data (crop_id, year, yield_amount, growth_rate) VALUES (?, ?, ?, ?)', 
                       (wheat_id, year, yield_amount, growth_rate))
    
    conn.commit()
    conn.close()
    print("Database population complete.")

if __name__ == '__main__':
    # Initialize Database
    create_database()
    init_database()
    
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Check if default port is in use
    default_port = 5002
    if not is_port_available(default_port):
        print(f"⚠️  Port {default_port} is already in use.")
        print(f"   Trying to find an available port...")
    
    # Try to find an available port
    port = default_port
    max_attempts = 10
    found_port = None
    
    for attempt in range(max_attempts):
        if is_port_available(port):
            found_port = port
            break
        port += 1
    
    if found_port is None:
        print(f"\n❌ Error: Could not find an available port. Tried ports {default_port}-{port-1}")
        print("\n   To free up port 5002, run:")
        print(f"   lsof -ti:{default_port} | xargs kill -9")
        print("\n   Or manually find and kill the process:")
        print(f"   lsof -i :{default_port}")
        exit(1)
    
    if found_port != default_port:
        print(f"✅ Using port {found_port} instead of {default_port}")
    
    print(f"\n{'='*50}")
    print(f"🚀 Flask server starting on port {found_port}")
    print(f"{'='*50}")
    print(f"\n🌐 Access the application at:")
    print(f"   http://localhost:{found_port}")
    print(f"   http://127.0.0.1:{found_port}")
    print(f"\n💡 Press CTRL+C to stop the server\n")
    print(f"{'='*50}\n")
    
    # Run Flask app
    try:
        app.run(host='0.0.0.0', port=found_port, debug=True, use_reloader=False)
    except OSError as e:
        print(f"\n❌ Error starting server: {e}")
        print(f"   Port {found_port} may have been taken by another process.")
        print(f"\n   Try killing the process:")
        print(f"   lsof -ti:{found_port} | xargs kill -9")
        exit(1)
    except KeyboardInterrupt:
        print(f"\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
