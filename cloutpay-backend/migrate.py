import sys
from dotenv import load_dotenv
load_dotenv()

from app.db import engine
from sqlalchemy import text

print("Starting migration...", flush=True)

with engine.begin() as conn:
    conn.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0'))
    conn.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0'))
    conn.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS last_payment_date DATE'))
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' ORDER BY column_name"))
    print('users columns:', [r[0] for r in result], flush=True)

print("Migration complete!", flush=True)
