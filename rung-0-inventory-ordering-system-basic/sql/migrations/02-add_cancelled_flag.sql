ALTER TABLE product_order
ADD COLUMN IF NOT EXISTS cancelled boolean DEFAULT false;