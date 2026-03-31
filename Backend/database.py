import aiosqlite

DATABASE_URL = "wasted.db"


async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL DEFAULT '',
                is_verified INTEGER NOT NULL DEFAULT 0,
                verification_token TEXT,
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
        # Migrate existing databases that are missing the new columns
        for migration in [
            "ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE users ADD COLUMN is_verified INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE users ADD COLUMN verification_token TEXT",
        ]:
            try:
                await db.execute(migration)
            except Exception:
                pass  # Column already exists
        await db.commit()


async def get_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        yield db
