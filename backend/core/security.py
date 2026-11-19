from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import HTTPException, Request
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select

from core.config import settings
from database.auth_connection import SessionLocal
from database.auth_models import User

HASHER = PasswordHash.recommended()
COOKIE = "storebridge_token"
BRANCHES = {"liberty", "galle_face", "pettah"}


def issue_token(user_id, role, version=0):
    if len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters")

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "role": role,
        "ver": version,
        "jti": uuid4().hex,
        "iat": now,
        "exp": now + timedelta(hours=8),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def set_cookie(response, token):
    response.set_cookie(
        COOKIE,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=8 * 3600,
        path="/",
    )


def current_user(request: Request):
    token = request.cookies.get(COOKIE)

    if not token:
        raise HTTPException(401, "Please sign in")

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
    except InvalidTokenError:
        raise HTTPException(401, "Session has expired. Please sign in again")

    if payload.get("role") == "demo" and payload.get("sub") == "demo":
        return {
            "id": "demo",
            "username": "demo",
            "name": "Portfolio Visitor",
            "role": "demo",
            "branch": None,
            "must_change_password": False,
            "session_id": payload["jti"],
        }

    with SessionLocal() as db:
        user = db.get(User, int(payload["sub"]))

        if not user or not user.active or user.token_version != payload.get("ver"):
            raise HTTPException(401, "Account inactive or session revoked")

        return {
            "id": user.id,
            "username": user.username,
            "name": user.full_name,
            "role": user.role,
            "branch": user.branch,
            "must_change_password": user.must_change_password,
            "session_id": payload["jti"],
        }


def admin_only(user):
    if user["role"] != "admin":
        raise HTTPException(403, "Only the owner may manage accounts")


def verified_password(password, stored):
    return HASHER.verify(password, stored)
