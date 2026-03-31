import os
from contextlib import asynccontextmanager
from datetime import datetime

import aiosqlite
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_db, init_db
from models import Token, UserCreate, UserLogin, UserOut, WalletData, WalletUpdate

load_dotenv()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Wasted API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3001").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=Token)
@limiter.limit("5/minute")
async def register(request: Request, body: UserCreate, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute(
        "SELECT id FROM users WHERE username = ?", (body.username,)
    ) as cur:
        if await cur.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")

    hashed = hash_password(body.password)
    async with db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (body.username, hashed),
    ) as cur:
        user_id = cur.lastrowid

    now = datetime.utcnow().isoformat()
    await db.execute(
        "INSERT INTO wallets (user_id, rate_per_minute, total_wasted, last_updated) VALUES (?, 0.0, 0.0, ?)",
        (user_id, now),
    )
    await db.commit()

    token = create_access_token({"sub": body.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, body: UserLogin, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?", (body.username,)
    ) as cur:
        row = await cur.fetchone()

    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token({"sub": row["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@app.get("/wallet", response_model=WalletData)
async def get_wallet(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    async with db.execute(
        "SELECT rate_per_minute, total_wasted, last_updated FROM wallets WHERE user_id = ?",
        (current_user["id"],),
    ) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {
        "rate_per_minute": row["rate_per_minute"],
        "total_wasted": row["total_wasted"],
        "last_updated": row["last_updated"],
    }


@app.put("/wallet")
async def update_wallet(
    body: WalletUpdate,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    fields: dict = {"last_updated": datetime.utcnow().isoformat()}
    if body.rate_per_minute is not None:
        fields["rate_per_minute"] = body.rate_per_minute
    if body.total_wasted is not None:
        fields["total_wasted"] = body.total_wasted

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    await db.execute(
        f"UPDATE wallets SET {set_clause} WHERE user_id = ?",
        (*fields.values(), current_user["id"]),
    )
    await db.commit()
    return {"ok": True}
