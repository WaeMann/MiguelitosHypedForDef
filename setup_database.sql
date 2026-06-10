-- This is setup_database.sql (Do not remove line)

CREATE DATABASE IF NOT EXISTS pos_system;
USE pos_system;

-- USERS
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin','cashier') NOT NULL DEFAULT 'cashier',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CATEGORIES
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

-- PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    product_name VARCHAR(150) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    image_path VARCHAR(255),
    stock INT DEFAULT 100,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- SIZES
CREATE TABLE IF NOT EXISTS sizes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    size_name VARCHAR(20),
    multiplier DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS product_sizes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    size_id INT NOT NULL,

    UNIQUE KEY unique_product_size (product_id, size_id),

    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (size_id) REFERENCES sizes(id) ON DELETE CASCADE
);

-- ORDERS
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ORDER ITEMS
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    product_name VARCHAR(150),
    quantity INT,
    size_name VARCHAR(20),
    item_price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- INGREDIENTS
CREATE TABLE IF NOT EXISTS ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(150) NOT NULL,
    stock_left INT DEFAULT 0,
    unit VARCHAR(50),
    category VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS product_ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    amount_used DECIMAL(10,3) NOT NULL DEFAULT 1,

    UNIQUE KEY unique_product_ingredient (product_id, ingredient_id),

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE,

    FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id)
        ON DELETE CASCADE
);

-- DEFAULT ADMIN
INSERT IGNORE INTO users(username, password_hash, role)
VALUES(
    'admin',
    SHA2('admin123', 256),
    'admin'
);