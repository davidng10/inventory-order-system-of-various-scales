CREATE TABLE IF NOT EXISTS products (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    name text NOT NULL,
    stock integer CHECK (stock > 0)
);

CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    name text NOT NULL
);

CREATE TABLE IF NOT EXISTS product_order (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    product_id uuid REFERENCES products,
    user_id uuid REFERENCES users,
    count integer
);
