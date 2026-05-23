-- seed_products.sql

USE pos_system;

-- Categories
INSERT INTO categories(category_name) VALUES
('Desserts'),

-- Sizes
INSERT INTO sizes(size_name,multiplier) VALUES
('12oz',1.0),
('16oz',1.3);

-- PRODUCTS
INSERT INTO products(category_id,product_name,base_price,image_path,stock) VALUES
(1,'Mango Ice Cream',35,'miguelitos_mangoicecream.png',100),
(1,'Hyped Mango',110,'miguelitos_hypedmango.png',100),
(1,'Mango Float',100,'miguelitos_mangofloat.png',100),
(1,'Mango Juice',80,'miguelitos_mangojuice.png',100),
(1,'Mango Shake',110,'miguelitos_mangoshake.png',100),
(1,'Mango Supreme',110,'miguelitos_mangosupreme.png',100),
