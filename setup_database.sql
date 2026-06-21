CREATE DATABASE IF NOT EXISTS pos_system;
USE pos_system;

-- ── USERS (with security columns) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    salt            VARCHAR(128) NOT NULL DEFAULT '',
    role            ENUM('admin','cashier') NOT NULL DEFAULT 'cashier',
    failed_attempts INT          NOT NULL DEFAULT 0,
    locked_until    BIGINT       NOT NULL DEFAULT 0,
    last_login      DATETIME     DEFAULT NULL,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ── CATEGORIES ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

-- ── PRODUCTS ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    category_id  INT,
    product_name VARCHAR(150) NOT NULL,
    description  VARCHAR(255) DEFAULT NULL,
    base_price   DECIMAL(10,2) NOT NULL,
    image_path   VARCHAR(255),
    stock        INT DEFAULT 100,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- ── SIZES ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sizes (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    size_name  VARCHAR(20),
    multiplier DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS product_sizes (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    size_id    INT NOT NULL,
    UNIQUE KEY unique_product_size (product_id, size_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (size_id)    REFERENCES sizes(id)    ON DELETE CASCADE
);

-- ── ORDERS ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    total           DECIMAL(10,2),
    discount_amount DECIMAL(10,2) DEFAULT 0,
    cash_paid       DECIMAL(10,2) DEFAULT NULL,
    change_given    DECIMAL(10,2) DEFAULT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── ORDER ITEMS ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    order_id     INT,
    product_id   INT,
    product_name VARCHAR(150),
    quantity     INT,
    size_name    VARCHAR(20),
    item_price   DECIMAL(10,2),
    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- ── INGREDIENTS ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ingredients (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(150) NOT NULL,
    stock_left      INT DEFAULT 0,
    unit            VARCHAR(50),
    category        VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS product_ingredients (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    product_id    INT NOT NULL,
    ingredient_id INT NOT NULL,
    amount_used   DECIMAL(10,3) NOT NULL DEFAULT 1,
    UNIQUE KEY unique_product_ingredient (product_id, ingredient_id),
    FOREIGN KEY (product_id)    REFERENCES products(id)    ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- ── LOGIN LOG ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS login_log (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50) NOT NULL,
    success    TINYINT     NOT NULL DEFAULT 0,
    reason     TEXT,
    session_id VARCHAR(64),
    logged_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── SESSION LOG ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS session_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    username    VARCHAR(50) NOT NULL,
    session_id  VARCHAR(64) NOT NULL,
    login_at    DATETIME    NOT NULL,
    logout_at   DATETIME,
    duration_s  INT,
    logout_type VARCHAR(30) DEFAULT 'manual',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── AUDIT LOG ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id   INT,
    username  VARCHAR(50) NOT NULL,
    action    VARCHAR(50) NOT NULL,
    detail    TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── DEFAULT ADMIN (SHA-256; auto-upgraded to PBKDF2 on first login) ───────
INSERT IGNORE INTO users (username, password_hash, role)
VALUES ('admin', SHA2('admin123', 256), 'admin'),
       ('Yngel', SHA2('Cutie@123', 256), 'admin'),
       ('cashier', SHA2('cashier123', 256), 'cashier');