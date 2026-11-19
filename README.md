# StoreBridge MCP — Walk & Talk Assistant

**Multi-branch mobile retail intelligence with a custom Model Context Protocol server.**

A fictionalized portfolio project based on a real retail workflow. All sales, products,
employees and financial values are **synthetic**, not Walk & Talk company records.

## Features

- Mobile-first React app with a polished desktop dashboard and chat.
- Owner login, branch manager login, and one-click recruiter demo.
- Owner: Overview, AI Assistant, Manage Users, Profile.
- Manager: AI Assistant and Profile. Managers can query stocks, selling prices,
  latest supplier-batch costs and low stock across all three branches.
- Demo: same read-only reports as the owner, **without** account administration.
- Owner creates managers; there is no self-registration.
- FastAPI authentication using HS256 JWT in an HttpOnly cookie and Argon2 hashing.
- Three separate PostgreSQL branch databases and one small auth database.
- One reusable FastMCP server with eight read-only tools for owner/demo;
  manager clients discover only three inventory/price tools.
- LangGraph supervisor routing + business tool-calling node; conversation history
  retained in the React session until page reload or New Chat.
- GPT-6 Luna primary, Gemini 3.8 Flash fallback; configured in `.env`.
- Optional Langfuse traces, with no LangSmith integration.
- Structured SQL calculations for revenue, COGS, margin, staff performance.
- Tables and charts within the chat; low-stock alerts and KPI summary.
- No purchase orders, transfers, edits or deletes of retail records.

## Project folders

```text
storebridge-mcp/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatWindow.jsx
│       │   ├── Overview.jsx
│       │   ├── ManageUsers.jsx
│       │   └── SalesChart.jsx
│       ├── api.js
│       ├── App.jsx
│       └── index.css
├── backend/
│   ├── agents/            # routing + LangGraph business agent
│   ├── core/              # config, model fallback, JWT security
│   ├── database/          # sessions, ORM, SQL queries, synthetic seed
│   ├── guardrails/        # input and response validation
│   ├── mcp_server/        # independent stdio MCP server
│   ├── prompts/           # natural business assistant instructions
│   ├── services/          # MCP client, chat, Langfuse
│   ├── tests/
│   ├── main.py
│   └── pyproject.toml
├── scripts/init-databases.sql
├── .env.example
└── README.md
```

## Run on Windows — NO DOCKER, NO PIP

Prerequisites: PostgreSQL (with pgAdmin), Python 3.11–3.13, uv, Node.js/npm.
If uv is not installed, use the official installer at https://docs.astral.sh/uv/getting-started/installation/.

### 1. Create four local PostgreSQL databases

Open pgAdmin → Postgres server → `postgres` database → Query Tool.
Create the role first, with your OWN local password (example below). If the role
already exists, do not create it again:

```sql
CREATE USER storebridge WITH PASSWORD 'YOUR_LOCAL_DB_PASSWORD';
```

Create the databases as four statements, one at a time in pgAdmin (PostgreSQL
CREATE DATABASE cannot run inside a transaction):

```sql
CREATE DATABASE walk_liberty OWNER storebridge;
CREATE DATABASE walk_ogf OWNER storebridge;
CREATE DATABASE walk_pettah OWNER storebridge;
CREATE DATABASE storebridge_auth OWNER storebridge;
```

No Docker Compose or cloud database is required.

### 2. Configure secrets

Open PowerShell in the extracted `storebridge-mcp` root:

```powershell
Copy-Item .env.example .env
```

Open `.env` in VS Code. Replace `CHANGE_ME` in **all four URLs** with your
actual PostgreSQL password. If the password contains characters such as `@`, `#`,
`/`, or `:`, URL-encode them in database URLs.

Also set:

```env
OPENAI_API_KEY=your_actual_key
GOOGLE_API_KEY=your_actual_gemini_key
OPENAI_MODEL=gpt-6-luna
GEMINI_MODEL=gemini-3.8-flash
OWNER_USERNAME=owner
OWNER_PASSWORD=your_strong_owner_password
JWT_SECRET=your_random_secret_at_least_32_chars_long
COOKIE_SECURE=false
```

On Windows, you can generate a random JWT secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Both requested model identifiers are configurable. API access and quota depend
on your provider accounts. If either is unavailable, update `.env` to an
accessible tool-calling model. Gemini is used only when the primary call fails.

### 3. Install backend and seed synthetic data

```powershell
cd backend
uv sync
uv run python -m database.seed
uv run python -m database.auth_seed
```

`uv sync` creates a local `.venv` automatically and installs the Python packages
from `pyproject.toml`. Commit the resulting `uv.lock` to Git once generated.

The business seed is intentionally destructive to demo data: **re-running it
recreates the branch transactions**, so don't use it for production records.
The auth seed only creates the owner if it doesn't exist.

### 4. Start FastAPI

Leave this terminal running:

```powershell
uv run uvicorn main:app --reload --port 8000
```

Health check: http://localhost:8000/api/health
Swagger: http://localhost:8000/docs

### 5. Start the React frontend

Open a NEW PowerShell terminal in the extracted project folder:

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**.

- Owner login: `OWNER_USERNAME` / `OWNER_PASSWORD` from `.env` (only on first seed).
- Try Demo: instant owner-level reporting over synthetic data, no admin actions.
- The owner can open **Manage Users** and create branch manager accounts.
- Managers sign in through the same page. They cannot see Overview or Manage Users.

### 6. Run tests

```powershell
cd backend
uv run pytest -q
```

Integration tests expect all three branch databases to be seeded.

### 7. Optional: enable Langfuse

Create a Langfuse project, get your credentials, and edit `.env`:

```env
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
LANGFUSE_TRACING_ENABLED=true
```

Restart FastAPI. Traces may include user prompts and business data, so enable
telemetry only with appropriate consent and a suitable data-retention policy.
There are no LangSmith keys or hooks.

## Suggested prompts

**Owner or Demo**

- Compare this month's revenue, gross profit and units sold for all branches.
- Who generated the highest sales revenue this month?
- Show the gross profit margin of phone accessories by category.
- Does Liberty Plaza have Samsung Galaxy S26 Ultra 256GB Black?
- How much does the same phone cost in Pettah?
- Do we have compatible accessories for that phone?

**Manager**

- Is Galaxy S26 Ultra 256GB Black available at One Galle Face?
- Compare iPhone 17 256GB Black stock, selling price and latest batch cost.
- Which phone cases and chargers are low on stock at Liberty Plaza?

## Architecture

```text
Browser (React)
  |-- JWT cookie--> FastAPI
  |                 |-- Owner Overview ---> controlled SQL analytics
  |                 |-- Manage Users -----> auth PostgreSQL
  |                 '-- Chat -> LangGraph -> role-scoped MCP client
  |                                       -> FastMCP stdio server
  |                                       -> SQLAlchemy read-only queries
  |                                           |-- walk_liberty
  |                                           |-- walk_ogf
  |                                           '-- walk_pettah
  '-- UI renders Markdown tables and charts
```

The supervisor routing node is deterministic to avoid an extra model roundtrip.
The business node makes model/tool calls. Reusing the MCP server in a second
compatible client is possible, but **do not expose it publicly** without
independent authentication and authorization.

## Understanding error codes

- **401**: No session, wrong password, expired JWT or revoked user session.
  Sign in again. A successful login is required before `/api/chat`.
- **403**: Real permission denial. Manager requesting `/api/overview` or
  `/api/managers` must be blocked. Demo visitors cannot change accounts.
  Inventory questions should work for managers; a manager has no financial MCP tools.
- **429**: Request limits protect demo API spending.
- **503**: PostgreSQL unavailable, invalid AI API key, model access issue,
  or MCP tool failure. Read the **FastAPI terminal traceback**, check local
  PostgreSQL service/URLs and API credentials. No code can guarantee zero 503s
  if a dependent service fails.
- If a chart has no rows, first check the date range and that you seeded data.

## Security and deployment notes

- This is a portfolio prototype, **not an audited production deployment**.
- Use HTTPS and `COOKIE_SECURE=true` when deployed.
- Prefer read-only PostgreSQL roles for the branch databases after seeding.
- JWT is signed; role and user status are re-validated against the auth DB.
- Public demo uses synthetic datasets and rate limits; hide or disable it
  before connecting actual business data.
- Manager MCP tool discovery and subprocess execution are scoped to that role.
- The frontend does not store JWTs in localStorage.
- Password changes invalidate outstanding JWTs (via token version).
- No financial data is available through manager MCP tools.
- The auth database uses write access only for account management;
  branch business tools only query existing records.
- Synthetic cost and margin numbers are for illustration; latest batch cost
  is not the cost of each remaining unit.

## Limitations and verification

Source files were syntax-checked. Live end-to-end behavior requires your
PostgreSQL server, installed npm/uv dependencies, and provider API credentials.
Model latency depends on live provider response times and tool execution.
The app avoids a second routing model call, and keeps MCP tool definitions
cached by role to reduce repeated startup overhead, but cannot promise
responses in a fixed number of seconds.
