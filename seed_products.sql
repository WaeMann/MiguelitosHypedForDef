-- This is seed_products.sql (Do not remove line)
-- Updated: Category is now used as the Available Size (e.g. "12oz", "16oz").
-- Add two entries per product — one per size — each as a separate product card.

USE pos_system;

-- ── SIZES (kept for the Change Order bar multipliers) ────────────────────────
INSERT INTO sizes(size_name, multiplier) VALUES
('12oz', 1.0),
('16oz', 1.3)
ON DUPLICATE KEY UPDATE multiplier = VALUES(multiplier);

-- ── CATEGORIES (each category = one available size) ──────────────────────────
INSERT INTO categories(category_name) VALUES
('12oz'),
('16oz');

-- ── PRODUCTS ─────────────────────────────────────────────────────────────────
-- Each product is listed twice — once per size category.
-- The base_price is set per-size so no multiplier is needed in the POS.
--   12oz prices   |   16oz prices  (~1.3×)

-- Mango Ice Cream
INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Ice Cream', 35, 'miguelitos_mangoicecream.png', 1
FROM categories WHERE category_name = '12oz';

INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Ice Cream', 46, 'miguelitos_mangoicecream.png', 1
FROM categories WHERE category_name = '16oz';

-- Hyped Mango
INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Hyped Mango', 110, 'miguelitos_hypedmango.png', 1
FROM categories WHERE category_name = '12oz';

INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Hyped Mango', 143, 'miguelitos_hypedmango.png', 1
FROM categories WHERE category_name = '16oz';

-- Mango Float
INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Float', 100, 'miguelitos_mangofloat.png', 1
FROM categories WHERE category_name = '12oz';

INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Float', 130, 'miguelitos_mangofloat.png', 1
FROM categories WHERE category_name = '16oz';

-- Mango Juice
INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Juice', 80, 'miguelitos_mangojuice.png', 1
FROM categories WHERE category_name = '12oz';

INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Juice', 104, 'miguelitos_mangojuice.png', 1
FROM categories WHERE category_name = '16oz';

-- Mango Shake
INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Shake', 110, 'miguelitos_mangoshake.png', 1
FROM categories WHERE category_name = '12oz';

INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Shake', 143, 'miguelitos_mangoshake.png', 1
FROM categories WHERE category_name = '16oz';

-- Mango Supreme
INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Supreme', 110, 'miguelitos_mangosupreme.png', 1
FROM categories WHERE category_name = '12oz';

INSERT INTO products(category_id, product_name, base_price, image_path, stock)
SELECT id, 'Mango Supreme', 143, 'miguelitos_mangosupreme.png', 1
FROM categories WHERE category_name = '16oz';

-- ── INGREDIENTS ──────────────────────────────────────────────────────────────
INSERT INTO ingredients(ingredient_name, stock_left, unit, category) VALUES
('Mango Soft Serve Mix',     20,  'kg',    'Soft Serve'),
('Mangoes 16oz Cup',         200, 'pcs',   'Cups'),
('Mangoes 12oz Cup',         250, 'pcs',   'Cups'),
('Dome Lid for 16oz Cups',   200, 'pcs',   'Lids'),
('Dome Lid for 12oz Cups',   250, 'pcs',   'Lids'),
('Giant Belgian Cone',       780, 'cones', 'Cone'),
('Fresh Mangoes',            3,   'kg',    'Fruit'),
('Crashed Graham',           4,   'pcs',   'Toppings'),
('Mango Syrup 1kg Gallon',   5,   'pcs',   'Syrup'),
('Mango Juice 1kg Gallon',   7,   'pcs',   'Juice'),
('All Purpose Cream',        10,  'pcs',   'Cream'),
('Condensada',               5,   'pcs',   'Milk'),
('Ice',                      20,  'kg',    'Miscellaneous'),
('Whipped Cream',            3,   'kg',    'Cream');