import os
import secrets
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
from email_service import send_verification_email
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


@app.post("/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, body: UserCreate, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute(
        "SELECT id FROM users WHERE username = ?", (body.username,)
    ) as cur:
        if await cur.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")

    async with db.execute(
        "SELECT id FROM users WHERE email = ?", (body.email,)
    ) as cur:
        if await cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(body.password)
    verification_token = secrets.token_urlsafe(32)

    async with db.execute(
        "INSERT INTO users (username, password_hash, email, is_verified, verification_token) VALUES (?, ?, ?, 0, ?)",
        (body.username, hashed, body.email, verification_token),
    ) as cur:
        user_id = cur.lastrowid

    now = datetime.utcnow().isoformat()
    await db.execute(
        "INSERT INTO wallets (user_id, rate_per_minute, total_wasted, last_updated) VALUES (?, 0.0, 0.0, ?)",
        (user_id, now),
    )
    await db.commit()

    await send_verification_email(body.email, body.username, verification_token)

    return {"message": "Verification email sent. Please check your inbox."}


@app.get("/auth/verify/{token}")
async def verify_email(token: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute(
        "SELECT id FROM users WHERE verification_token = ? AND is_verified = 0", (token,)
    ) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=400, detail="Invalid or already used verification link")

    await db.execute(
        "UPDATE users SET is_verified = 1, verification_token = NULL WHERE id = ?",
        (row["id"],),
    )
    await db.commit()
    return {"message": "Email verified"}


@app.post("/auth/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, body: UserLogin, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute(
        "SELECT id, username, password_hash, is_verified FROM users WHERE username = ?", (body.username,)
    ) as cur:
        row = await cur.fetchone()

    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not row["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in",
        )

    token = create_access_token({"sub": row["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=UserOut)
async def get_me(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    async with db.execute(
        "SELECT id, username, email, is_verified FROM users WHERE id = ?",
        (current_user["id"],),
    ) as cur:
        row = await cur.fetchone()
    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "is_verified": bool(row["is_verified"]),
    }


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
