import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from core.config import settings
from core.security import (
    BRANCHES,
    COOKIE,
    HASHER,
    admin_only,
    current_user,
    issue_token,
    set_cookie,
    verified_password,
)
from database import queries
from database.auth_connection import SessionLocal
from database.auth_models import AuditLog, User
from guardrails.input_guard import validate_messages
from schemas import (
    ChatRequest,
    LoginRequest,
    ManagerCreate,
    ManagerUpdate,
    MyPasswordChange,
    PasswordReset,
)
from services.chat import respond

logger = logging.getLogger("storebridge")
app = FastAPI(title="StoreBridge MCP | Walk & Talk Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)

attempts = defaultdict(deque)


def limit(key, count, seconds=3600):
    now = datetime.now(timezone.utc)
    events = attempts[key]

    while events and now - events[0] > timedelta(seconds=seconds):
        events.popleft()

    if len(events) >= count:
        raise HTTPException(429, "Request limit reached. Please try later")

    events.append(now)


def safe_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "name": user.full_name,
        "role": user.role,
        "branch": user.branch,
        "active": user.active,
        "must_change_password": user.must_change_password,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Walk & Talk Assistant"}


@app.post("/api/auth/login")
def login(body: LoginRequest, request: Request, response: Response):
    address = request.client.host if request.client else "unknown"
    limit(f"login:{address}", 12, 900)

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == body.username))

        if not user or not user.active:
            raise HTTPException(401, "Incorrect username or password")

        if not verified_password(body.password, user.password_hash):
            raise HTTPException(401, "Incorrect username or password")

        set_cookie(response, issue_token(user.id, user.role, user.token_version))
        return safe_user(user)


@app.post("/api/auth/demo")
def demo(request: Request, response: Response):
    address = request.client.host if request.client else "unknown"
    limit(f"demo-start:{address}", 15, 3600)

    set_cookie(response, issue_token("demo", "demo"))

    return {
        "id": "demo",
        "username": "demo",
        "name": "Portfolio Visitor",
        "role": "demo",
        "branch": None,
    }


@app.get("/api/auth/me")
def me(user=Depends(current_user)):
    return user


@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"status": "signed_out"}


@app.post("/api/auth/change-password")
def change_password(body: MyPasswordChange, user=Depends(current_user)):
    if user["role"] == "demo":
        raise HTTPException(403, "Demo account has no password")

    with SessionLocal.begin() as db:
        record = db.get(User, user["id"])

        if not verified_password(body.current_password, record.password_hash):
            raise HTTPException(400, "Current password is incorrect")

        record.password_hash = HASHER.hash(body.new_password)
        record.must_change_password = False
        record.token_version += 1
        db.add(AuditLog(actor_id=record.id, action="change_password", target=record.username))

    return {"status": "password_changed", "reauthenticate": True}


@app.get("/api/overview")
def overview(user=Depends(current_user)):
    if user["role"] not in {"admin", "demo"}:
        raise HTTPException(403, "Overview is available to the owner only")

    try:
        summary = queries.sales_summary()
        stock = queries.inventory_insights()
        people = queries.employee_performance()

        return {
            **summary,
            "low_stock_count_shown": len(stock["low_stock"]),
            "low_stock_products": stock["low_stock"][:6],
            "top_salespeople": people["ranking"][:5],
            "demo_data": True,
        }

    except Exception:
        logger.exception("Overview query failed")
        raise HTTPException(503, "Database unavailable. Verify PostgreSQL and seed data")


@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request, user=Depends(current_user)):
    address = request.client.host if request.client else "unknown"
    identity = user["session_id"]

    if user["role"] == "demo":
        limit(f"demo:{address}", settings.max_demo_requests_per_hour)
    else:
        limit(f"chat:{identity}", 150)

    try:
        validate_messages(body.messages)
        return await respond(body.messages, user["role"])

    except ValueError as error:
        raise HTTPException(400, str(error))

    except Exception:
        logger.exception("Chat execution failed")
        raise HTTPException(
            503,
            "The assistant could not verify this answer. Check the server logs, database connection and AI API keys.",
        )


@app.get("/api/managers")
def list_managers(user=Depends(current_user)):
    admin_only(user)

    with SessionLocal() as db:
        records = db.scalars(
            select(User).where(User.role == "manager").order_by(User.id)
        ).all()

        return [safe_user(record) for record in records]


@app.post("/api/managers", status_code=201)
def create_manager(body: ManagerCreate, user=Depends(current_user)):
    admin_only(user)

    if body.branch not in BRANCHES:
        raise HTTPException(400, "Invalid branch")

    with SessionLocal.begin() as db:
        existing = db.scalar(select(User).where(User.username == body.username))

        if existing:
            raise HTTPException(409, "Username already exists")

        manager = User(
            username=body.username,
            full_name=body.full_name,
            password_hash=HASHER.hash(body.password),
            role="manager",
            branch=body.branch,
            active=True,
            must_change_password=True,
        )

        db.add(manager)
        db.flush()
        db.add(AuditLog(actor_id=user["id"], action="create_manager", target=manager.username))
        result = safe_user(manager)

    return result


@app.patch("/api/managers/{manager_id}")
def update_manager(manager_id: int, body: ManagerUpdate, user=Depends(current_user)):
    admin_only(user)

    if body.branch is not None and body.branch not in BRANCHES:
        raise HTTPException(400, "Invalid branch")

    with SessionLocal.begin() as db:
        manager = db.get(User, manager_id)

        if not manager or manager.role != "manager":
            raise HTTPException(404, "Manager not found")

        if body.branch is not None:
            manager.branch = body.branch

        if body.active is not None:
            manager.active = body.active

        manager.token_version += 1
        db.add(AuditLog(actor_id=user["id"], action="update_manager", target=manager.username))
        result = safe_user(manager)

    return result


@app.post("/api/managers/{manager_id}/reset-password")
def reset_manager_password(
    manager_id: int,
    body: PasswordReset,
    user=Depends(current_user),
):
    admin_only(user)

    with SessionLocal.begin() as db:
        manager = db.get(User, manager_id)

        if not manager or manager.role != "manager":
            raise HTTPException(404, "Manager not found")

        manager.password_hash = HASHER.hash(body.new_password)
        manager.must_change_password = True
        manager.token_version += 1
        db.add(AuditLog(actor_id=user["id"], action="reset_password", target=manager.username))

    return {"status": "password_reset"}
