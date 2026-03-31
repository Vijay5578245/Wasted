import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

_USERNAME_RE = re.compile(r'^[a-zA-Z0-9_.\-]+$')
_PASSWORD_RE = re.compile(r"^[a-zA-Z0-9!@#$%^&*()\-_=+\[\]{};:'\",.<>?/\\|`~]+$")


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('username')
    @classmethod
    def username_chars(cls, v: str) -> str:
        if not _USERNAME_RE.match(v):
            raise ValueError('Only letters, numbers, underscores, dots and hyphens allowed')
        return v

    @field_validator('password')
    @classmethod
    def password_chars(cls, v: str) -> str:
        if not _PASSWORD_RE.match(v):
            raise ValueError('Password contains unsupported characters')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    username: str


class WalletData(BaseModel):
    rate_per_minute: float
    total_wasted: float
    last_updated: str


class WalletUpdate(BaseModel):
    rate_per_minute: Optional[float] = None
    total_wasted: Optional[float] = None
