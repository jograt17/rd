CREATE SCHEMA IF NOT EXISTS avoria;
SET search_path TO avoria;
CREATE TABLE products(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    price DECIMAL(10, 2) CHECK (price > 0),
    stock_quantity INT CHECK (stock_quantity >= 0),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TYPE order_status AS ENUM ('pending', 'completed', 'cancelled');
CREATE TABLE orders(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2),
    status order_status DEFAULT 'pending',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE order_item(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT REFERENCES products(id) ON DELETE CASCADE,
    quantity INT CHECK (quantity > 0),
    unit_price DECIMAL(10, 2),
    subtotal DECIMAL(10, 2)
);