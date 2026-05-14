from dotenv import load_dotenv
load_dotenv()
from app.db import engine
from sqlalchemy import inspect, text

insp = inspect(engine)
cols = [c['name'] for c in insp.get_columns('payment_orders')]
print('payment_orders columns:', cols, flush=True)

# Also run the ALTER just in case
with engine.begin() as conn:
    conn.execute(text('ALTER TABLE payment_orders ADD COLUMN IF NOT EXISTS guest_session_id VARCHAR'))
    print('ALTER done', flush=True)

cols2 = [c['name'] for c in inspect(engine).get_columns('payment_orders')]
print('after alter:', cols2, flush=True)
