-- Initialize database for Telegram Bar Bot
-- This script creates all necessary tables and initial data

-- Create loyalty_levels table
CREATE TABLE IF NOT EXISTS loyalty_levels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    threshold FLOAT NOT NULL,
    points_rate FLOAT NOT NULL,
    "order" INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create menu_categories table
CREATE TABLE IF NOT EXISTS menu_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    "order" INTEGER NOT NULL
);

-- Create users table (with BIGINT for telegram_id)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    wallet VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    loyalty_points FLOAT NOT NULL DEFAULT 0.0,
    total_spent FLOAT NOT NULL DEFAULT 0.0,
    loyalty_level_id INTEGER NOT NULL,
    referrer_id INTEGER,
    referral_code VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loyalty_level_id) REFERENCES loyalty_levels(id),
    FOREIGN KEY (referrer_id) REFERENCES users(id)
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS ix_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS ix_users_referral_code ON users(referral_code);

-- Create menu_items table
CREATE TABLE IF NOT EXISTS menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    image_url VARCHAR(500),
    category_id INTEGER NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES menu_categories(id)
);

-- Create index for menu_items table
CREATE INDEX IF NOT EXISTS ix_menu_items_category_id ON menu_items(category_id);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    total_amount FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create index for orders table
CREATE INDEX IF NOT EXISTS ix_orders_user_id ON orders(user_id);

-- Create promotions table
CREATE TABLE IF NOT EXISTS promotions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(500),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price FLOAT NOT NULL,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Create index for order_items table
CREATE INDEX IF NOT EXISTS ix_order_items_order_id ON order_items(order_id);

-- Create points_transactions table
CREATE TABLE IF NOT EXISTS points_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    order_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create index for points_transactions table
CREATE INDEX IF NOT EXISTS ix_points_transactions_user_id ON points_transactions(user_id);

-- Insert initial loyalty levels
INSERT INTO loyalty_levels (name, threshold, points_rate, "order", created_at, updated_at) VALUES
    ('Bronze', 0.0, 5.0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Silver', 1000.0, 7.0, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Gold', 5000.0, 10.0, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Platinum', 10000.0, 15.0, 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Insert initial menu categories
INSERT INTO menu_categories (name, "order") VALUES
    ('Напитки', 1),
    ('Коктейли', 2),
    ('Закуски', 3),
    ('Горячие блюда', 4),
    ('Десерты', 5)
ON CONFLICT DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_loyalty_levels_updated_at BEFORE UPDATE ON loyalty_levels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_menu_items_updated_at BEFORE UPDATE ON menu_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();