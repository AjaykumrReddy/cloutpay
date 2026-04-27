CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    display_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users (phone_number);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at);
CREATE INDEX IF NOT EXISTS idx_phone_created ON users (phone_number, created_at);

-- Add share_token to existing tables (safe to run multiple times)
ALTER TABLE users ADD COLUMN IF NOT EXISTS share_token VARCHAR(16) UNIQUE;
UPDATE users SET share_token = encode(gen_random_bytes(8), 'base64') WHERE share_token IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_share_token ON users (share_token);

CREATE TABLE IF NOT EXISTS otps (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) NOT NULL,
    code VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_otps_phone_number ON otps (phone_number);

CREATE TABLE IF NOT EXISTS payment_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    razorpay_order_id VARCHAR UNIQUE,
    amount INTEGER NOT NULL,
    currency VARCHAR DEFAULT 'INR',
    status VARCHAR DEFAULT 'created',
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_payment_orders_razorpay_order_id ON payment_orders (razorpay_order_id);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES payment_orders(id),
    razorpay_payment_id VARCHAR UNIQUE,
    user_name VARCHAR NOT NULL,
    amount INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments (created_at);
CREATE INDEX IF NOT EXISTS idx_payments_razorpay_payment_id ON payments (razorpay_payment_id);

CREATE TABLE IF NOT EXISTS hall_of_fame (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    total_amount INTEGER NOT NULL,
    month VARCHAR(7) UNIQUE NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hall_of_fame_month ON hall_of_fame (month);
