import os
import aiosqlite

DATABASE_URL = os.getenv("DATABASE_URL", "wasted.db")


async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                rate_per_minute REAL NOT NULL DEFAULT 0.0,
                total_wasted REAL NOT NULL DEFAULT 0.0,
                last_updated TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        # Drop legacy columns that are no longer used
        for migration in [
            "ALTER TABLE users DROP COLUMN email",
            "ALTER TABLE users DROP COLUMN is_verified",
            "ALTER TABLE users DROP COLUMN verification_token",
        ]:
            try:
                await db.execute(migration)
            except Exception:
                pass  # Column doesn't exist or already dropped
        await db.commit()


async def get_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        yield db
