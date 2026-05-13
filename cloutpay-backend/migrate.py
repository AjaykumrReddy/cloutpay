import sys
from dotenv import load_dotenv
load_dotenv()

from app.db import engine
from sqlalchemy import text

print("Starting migration...", flush=True)

with engine.begin() as conn:
    conn.execute(text('ALTER TABLE payment_orders ALTER COLUMN razorpay_order_id DROP NOT NULL'))
    result = conn.execute(text("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name='payment_orders' AND column_name='razorpay_order_id'"))
    for r in result:
        print(dict(r._mapping))
    print('Done', flush=True)

print("Migration complete!", flush=True)
