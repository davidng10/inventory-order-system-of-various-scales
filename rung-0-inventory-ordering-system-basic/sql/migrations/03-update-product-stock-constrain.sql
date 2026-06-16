ALTER TABLE products
DROP CONSTRAINT products_stock_check;

ALTER TABLE products
ADD CONSTRAINT products_stock_check CHECK (stock >= 0);