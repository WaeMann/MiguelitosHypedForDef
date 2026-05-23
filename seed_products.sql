-- seed_products.sql

USE pos_system;

-- Categories
INSERT INTO categories(category_name) VALUES
('Desserts');

-- Sizes
INSERT INTO sizes(size_name, multiplier) VALUES
('12oz', 1.0),
('16oz', 1.3);

-- Products
INSERT INTO products(category_id, product_name, base_price, image_path, stock) VALUES
(1, 'Mango Ice Cream',  35,  'miguelitos_mangoicecream.png',  100),
(1, 'Hyped Mango',      110, 'miguelitos_hypedmango.png',     100),
(1, 'Mango Float',      100, 'miguelitos_mangofloat.png',     100),
(1, 'Mango Juice',      80,  'miguelitos_mangojuice.png',     100),
(1, 'Mango Shake',      110, 'miguelitos_mangoshake.png',     100),
(1, 'Mango Supreme',    110, 'miguelitos_mangosupreme.png',   100);

-- Ingredients
INSERT INTO ingredients(ingredient_name, stock_left, unit, category) VALUES
('Mango Soft Serve Mix 1kg', 24,  'pcs',   'Soft Serve'),
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
('Condensada',               5,   'pcs',   'Milk');