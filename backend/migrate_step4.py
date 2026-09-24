from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE manuscripts ADD COLUMN IF NOT EXISTS english_translation TEXT;"))
    conn.execute(text("ALTER TABLE manuscripts ADD COLUMN IF NOT EXISTS translation_status VARCHAR DEFAULT 'pending';"))
    conn.commit()

print("PostgreSQL columns for English Translation verified/added.")
