-- Create Database
CREATE DATABASE pos_system;
USE pos_system;

-- =========================
-- 0. Users Table
-- =========================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'cashier') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Default Accounts (Passwords: admin123 and register1)
INSERT INTO users (username, password_hash, role) VALUES 
('admin', SHA2('admin123', 256), 'admin'),
('cashier', SHA2('register1', 256), 'cashier');

-- =========================
-- 1. Inventory Table (Updated)
-- =========================
CREATE TABLE inventory (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    available_sizes VARCHAR(100), 
    flavors VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- 2. Sales / Orders Table
-- =========================
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity_sold INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES inventory(product_id)
);

-- =========================
-- 3. Inventory History (Tracking changes)
-- =========================
CREATE TABLE inventory_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    change_type ENUM('ADD', 'REMOVE', 'SALE'),
    quantity_changed INT,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES inventory(product_id)
);

-- =========================
-- 4. Daily Report View
-- =========================
CREATE VIEW daily_report AS
SELECT 
    DATE(sale_date) AS day,
    SUM(total_price) AS total_income,
    SUM(quantity_sold) AS total_items_sold
FROM sales
GROUP BY DATE(sale_date);

-- =========================
-- 5. Weekly Report View
-- =========================
CREATE VIEW weekly_report AS
SELECT 
    YEARWEEK(sale_date, 1) AS week,
    SUM(total_price) AS total_income,
    SUM(quantity_sold) AS total_items_sold
FROM sales
GROUP BY YEARWEEK(sale_date, 1);

-- =========================
-- 6. Monthly Report View
-- =========================
CREATE VIEW monthly_report AS
SELECT 
    DATE_FORMAT(sale_date, '%Y-%m') AS month,
    SUM(total_price) AS total_income,
    SUM(quantity_sold) AS total_items_sold
FROM sales
GROUP BY DATE_FORMAT(sale_date, '%Y-%m');

-- =========================
-- 7. Income Trend Analysis View
-- =========================
CREATE VIEW income_trend AS
SELECT 
    sale_date,
    total_price,
    SUM(total_price) OVER (ORDER BY sale_date) AS cumulative_income
FROM sales;

-- =========================
-- 8. Sample Insert
-- =========================
INSERT INTO inventory (product_name, quantity, oz, price)
VALUES 
('Product A', 100, 12.5, 50.00),
('Product B', 200, 8.0, 30.00);