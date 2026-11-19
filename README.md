
# StoreBridge MCP — Walk & Talk Assistant

### Agentic AI for Multi-Branch Retail Intelligence

An AI-powered retail intelligence platform that connects independent branch databases and enables business owners to monitor inventory, compare prices, analyze sales, and make informed decisions through natural language conversations.

Built with **LangGraph, Model Context Protocol (MCP), FastAPI, PostgreSQL, and React**.

> **Portfolio Project:** StoreBridge MCP is a fictionalized implementation inspired by real mobile retail workflows. All product quantities, sales transactions, employee records, and financial figures are synthetic and do not represent actual Walk & Talk business data.

---

## The Problem

Managing multiple retail branches independently creates significant operational challenges.

A business owner may need to contact individual branches to check stock availability, compare selling prices, or request sales reports.

This often leads to:

- Limited visibility into inventory across branches.
- Time-consuming stock availability checks.
- Fragmented sales and financial reporting.
- Difficulty comparing branch performance.
- Delayed decision-making due to disconnected databases.

**The challenge:** How can a business owner access accurate information from multiple independent branch databases without switching between different systems?

## The Solution

**StoreBridge MCP** addresses this problem through a centralized, conversational retail intelligence platform.

Instead of manually checking different databases, the owner can ask questions such as:

- "Which branch has the most Samsung Galaxy S26 Ultra stock?"
- "Compare the selling prices across all three branches."
- "Which branch generated the highest revenue last month?"
- "Who was our top-performing salesperson?"
- "What products are running low at One Galle Face?"

The assistant interprets each question, selects appropriate MCP tools, retrieves information from authorized databases, and presents the results in natural language, tables, or charts.

Business calculations are performed using structured SQL and backend logic rather than relying on the LLM to invent figures.

---

## Key Features

### 1. Conversational Business Intelligence

Ask questions about inventory, product pricing, sales, profitability, and business performance using everyday language.

The assistant supports contextual follow-up questions.

**Example conversation:**

**Owner:** Do we have Samsung Galaxy S26 Ultra 256GB Black?

**Assistant:** Retrieves stock availability across the branches.

**Owner:** What about Pettah?

**Assistant:** Understands that the question refers to the same phone variant and checks the Pettah branch.

**Owner:** Compare the selling prices.

**Assistant:** Retrieves and compares relevant prices without requiring the owner to repeat the product details.

### 2. Multi-Branch Inventory Visibility

The system connects three independently managed PostgreSQL branch databases:

| Branch | Location |
|---|---|
| Liberty Plaza | Kollupitiya, Colombo |
| One Galle Face Mall | Colombo |
| Pettah Main Street | Colombo |

Supported inventory capabilities include:

- Product availability searches.
- Cross-branch stock comparisons.
- Selling-price comparisons.
- Purchase-cost information.
- Product variant identification.
- Low-stock monitoring.
- Mobile accessories availability.

### 3. Business Performance Analytics

Authorized owner-level users can access:

- Sales revenue by branch.
- Monthly and daily sales reports.
- Gross profit and margin analysis.
- Product-category performance.
- Branch revenue comparisons.
- Employee sales performance.
- Inventory-related business insights.

Business metrics are calculated from database records using SQLAlchemy and backend queries.

### 4. MCP-Powered Database Access

A custom **FastMCP server** exposes reusable read-only business tools.

The LangGraph business agent dynamically selects tools according to the owner's question.

MCP separates business-data access from the conversational reasoning layer, making the tool interface reusable by compatible clients.

The application does not allow inventory modification, transaction deletion, or stock updates through its conversational tools.

### 5. LangGraph Multi-Agent Workflow

The application uses a LangGraph-based architecture consisting of:

**Supervisor Agent**
- Interprets user intent using an LLM.
- Identifies business-related questions.
- Recognizes unrelated requests.
- Detects requests to modify business records.
- Routes requests to the appropriate workflow.

**Business Agent**
- Understands the business question.
- Selects relevant MCP tools.
- Interprets returned data.
- Generates clear, grounded answers.
- Supports contextual follow-up questions.

**Guardrails**
- Domain-specific request handling.
- Read-only business operations.
- Role-based permissions.
- Input and output validation.
- Controlled responses to unsupported requests.

### 6. Role-Based Access Control

StoreBridge MCP supports three access levels.

| Capability | Owner | Branch Manager | Demo |
|---|:---:|:---:|:---:|
| Cross-branch inventory | Yes | Yes | Yes |
| Selling prices | Yes | Yes | Yes |
| Purchase costs | Yes | Yes | Yes |
| Low-stock information | Yes | Yes | Yes |
| Revenue analytics | Yes | No | Yes |
| Gross profit analytics | Yes | No | Yes |
| Employee performance | Yes | No | Yes |
| Manage user accounts | Yes | No | No |

**Owner**
- Full access to business intelligence.
- Creates and manages branch manager accounts.
- Can access financial and operational reports.

**Branch Manager**
- Accesses authorized inventory and pricing information.
- Cannot access owner-only financial reports.
- Cannot administer user accounts.

**Demo User**
- Can explore synthetic owner-level business information.
- Cannot create or modify manager accounts.

Permissions are enforced by the backend and role-scoped MCP tool access, not merely hidden frontend elements.

### 7. Interactive Dashboard and Chat

The React application includes:

- Owner overview dashboard.
- AI-powered business chat.
- Markdown tables and visualizations.
- Branch performance charts.
- Manager account administration.
- User profile.
- Responsive desktop and mobile layouts.

---

## System Architecture

The system separates the user interface, AI orchestration, tool execution, and business databases.

```text
                    React Frontend
                          |
                          v
                    FastAPI Backend
                          |
             Authentication & Authorization
                          |
                          v
                   LangGraph Workflow
                          |
                   Supervisor Agent
                          |
             +------------+-------------+
             |            |             |
             v            v             v
        Business       Out-of-Scope    Read-Only
         Request        Response       Refusal
             |
             v
        Business Agent
             |
             v
        MCP Tool Client
             |
             v
       Custom FastMCP Server
             |
             v
       SQLAlchemy Queries
             |
       +-----+------+------+
       |            |      |
       v            v      v
   Liberty DB    OGF DB  Pettah DB

         Separate Auth PostgreSQL
                 Database
```

**Observability:** Langfuse is integrated with the LangGraph workflow for tracing and debugging.

**Evaluation:** Ragas is used to evaluate responses against a golden question-and-reference dataset.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend API | FastAPI, Python |
| Agent Orchestration | LangGraph |
| Tool Integration | FastMCP, MCP |
| LLM Integration | OpenAI, Google Gemini |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT, HttpOnly Cookies, Argon2 |
| Observability | Langfuse |
| Evaluation | Ragas, Pandas |
| Package Management | uv, npm |
| Version Control | Git, GitHub |

Model identifiers and provider credentials are configurable through environment variables. Availability depends on the relevant API account.

---

## AI Evaluation

The assistant was evaluated using **Ragas** against a custom 25-question golden dataset designed for the owner role.

The evaluation covers:

- Product and variant identification.
- Cross-branch inventory availability.
- Headphones and mobile accessories.
- Selling-price comparisons.
- Branch revenue reporting.
- Gross profit analysis.
- Employee sales performance.
- Ambiguous requests.
- Out-of-scope questions.
- Unauthorized modification requests.

### Ragas Results

| Evaluation Metric | Score |
|---|---:|
| Faithfulness | **0.895** |
| Context Precision | **0.523** |
| Context Recall | **0.841** |

### Interpretation

**Faithfulness — 89.5%**

Most claims in evaluated assistant responses were supported by the retrieved MCP evidence.

**Context Precision — 52.3%**

Some retrieved tool outputs contained information beyond what was required for the reference answer, indicating an opportunity to improve context relevance and retrieval efficiency.

**Context Recall — 84.1%**

The retrieved evidence covered much of the information required by the golden reference answers.

### Evaluation Limitations

These results represent eligible MCP-grounded responses rather than all 25 questions.

Requests that do not require database retrieval, including unrelated questions and inventory modification refusals, were excluded from the context-based metrics.

The system uses structured MCP database tools rather than a traditional vector-based retriever. Consequently, context precision and recall should be interpreted with that distinction in mind.

The evaluation results provide a baseline for further improvements.

---

## Security and Access Control

Security is implemented across authentication, authorization, and data-access layers.

Key mechanisms include:

- JWT-based authentication using HttpOnly cookies.
- Argon2 password hashing.
- Owner-controlled manager account creation.
- Role-scoped MCP tool access.
- Server-side authorization checks.
- Restricted financial analytics.
- Read-only business database tools.
- Session invalidation after account changes.
- No public user registration.
- Environment-based secret management.

The application does not expose database-modification tools through the assistant.

**Note:** This is a portfolio prototype, not an independently audited production system.

---

## Project Structure

```text
storebridge-mcp/
|
|-- backend/
|   |-- agents/
|   |   |-- supervisor.py
|   |   |-- business_agent.py
|   |   `-- graph.py
|   |
|   |-- core/
|   |-- database/
|   |-- guardrails/
|   |-- mcp_server/
|   |-- prompts/
|   |-- services/
|   |
|   |-- evals/
|   |   |-- ragas_eval.py
|   |   `-- Walk_and_Talk_Owner_Golden_25_REVISED.csv
|   |
|   |-- main.py
|   |-- pyproject.toml
|   `-- uv.lock
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- api.js
|   |   |-- App.jsx
|   |   `-- index.css
|   |
|   |-- package.json
|   `-- vite.config.js
|
|-- scripts/
|   `-- init-databases.sql
|
|-- .env.example
|-- .gitignore
`-- README.md
```

---

## Getting Started

### Prerequisites

Install the following:

- Python 3.11 or newer, compatible with the locked dependencies.
- PostgreSQL.
- Node.js and npm.
- uv Python package manager.
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/storebridge-mcp.git
cd storebridge-mcp
```

Replace `YOUR_USERNAME` with the GitHub account that hosts the repository.

### 2. Configure PostgreSQL

Create four PostgreSQL databases:

```text
walk_liberty
walk_ogf
walk_pettah
storebridge_auth
```

These databases store the independent branch records and authentication information.

Using pgAdmin or psql, create them with an authorized PostgreSQL account.

### 3. Configure Environment Variables

Copy the provided example environment configuration:

```powershell
Copy-Item .env.example .env
```

Update your local `.env` with your PostgreSQL connection URLs, model API keys, JWT secret, and owner credentials.

Example:

```dotenv
LIBERTY_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/walk_liberty

GALLE_FACE_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/walk_ogf

PETTAH_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/walk_pettah

AUTH_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/storebridge_auth

OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_gemini_api_key

OPENAI_MODEL=your_available_openai_model
GEMINI_MODEL=your_available_gemini_model

OWNER_USERNAME=owner
OWNER_PASSWORD=your_owner_password

JWT_SECRET=your_random_jwt_secret
COOKIE_SECURE=false
```

Use URL-encoded passwords in database connection URLs when necessary.

**Never commit your actual `.env` file or API credentials to GitHub.**

### 4. Install Backend Dependencies

From the repository root:

```powershell
cd backend
uv sync
```

### 5. Initialize Synthetic Databases

Run the database seed scripts:

```powershell
uv run python -m database.seed
uv run python -m database.auth_seed
```

The seed scripts populate the demonstration databases and initialize the owner account.

**Warning:** The business seed regenerates synthetic business records. Do not rerun it against data you wish to preserve.

### 6. Start FastAPI

```powershell
uv run uvicorn main:app --reload --port 8000
```

Backend endpoints:

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### 7. Start React

Open another terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Visit:

**http://localhost:5173**

Sign in using the configured owner credentials or use the demo option.

---

## Running the Ragas Evaluation

The evaluation script is located at:

```text
backend/evals/ragas_eval.py
```

From the `backend` directory:

```powershell
uv run python -m evals.ragas_eval
```

The evaluation workflow:

1. Loads the 25-question golden CSV.
2. Authenticates the owner account when generating new answers.
3. Runs business questions through LangGraph.
4. Collects MCP tool evidence.
5. Evaluates eligible responses with Ragas.
6. Saves evaluation results to CSV.

Generated results can include:

```text
backend/evals/assistant_responses.csv
backend/evals/ragas_results.csv
```

The evaluation configuration supports reusing saved assistant responses to avoid repeated MCP queries.

---

## Observability with Langfuse

StoreBridge MCP supports Langfuse tracing for AI workflow monitoring.

Langfuse helps inspect:

- Agent execution traces.
- LLM calls.
- MCP tool interactions.
- Response latency.
- Model usage and debugging information.

To configure Langfuse, create a project in Langfuse Cloud and add the credentials to `.env`:

```dotenv
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
LANGFUSE_TRACING_ENABLED=true
```

Use the correct regional Langfuse URL for your account.

Trace visibility depends on the configured observability callbacks and the availability of the Langfuse service.

Do not log secrets or sensitive customer information.

---

## Example Questions

### Inventory

- Do we have Samsung Galaxy S26 Ultra 256GB Black?
- Which branch has the highest available stock?
- Compare stock availability across all branches.
- Are Sony WH-CH520 headphones available?
- Which accessories are available for the S26 Ultra?

### Pricing

- Compare selling prices for the same phone across our branches.
- Which branch has the lowest price for Sony WH-CH520?
- What is the latest recorded purchase cost of this product?

### Business Analytics

- Which branch generated the highest revenue last month?
- Show yesterday's branch-wise sales.
- What was our total gross profit last month?
- Who generated the highest sales revenue?
- Which product categories contribute the most revenue?

### Guardrail Tests

- What is Python?
- Delete Samsung Galaxy S26 Ultra inventory records.
- Add 20 headphones to the Liberty Plaza database.

The assistant should redirect unrelated questions and refuse unauthorized modifications while continuing to support legitimate business queries.

---

## Engineering Decisions

### Why MCP?

MCP provides a standardized interface between the AI agent and external business tools.

Instead of embedding database access directly into the assistant's prompts, StoreBridge exposes controlled business functionality through a reusable MCP server.

### Why LangGraph?

LangGraph provides structured orchestration for intent classification, agent execution, tool calls, and conversation flow.

It also allows business questions, unrelated requests, and modification attempts to follow separate paths.

### Why Separate PostgreSQL Databases?

The system models a realistic environment where individual retail branches maintain independent operational records.

This demonstrates cross-database business intelligence without merging all branch data into a single database.

### Why Deterministic SQL Calculations?

Financial accuracy is essential.

Revenue, profit, inventory quantities, and other numerical business metrics are computed using database records and backend logic.

The LLM is responsible for understanding questions and explaining results, not inventing calculations.

### Why Ragas?

Ragas provides a repeatable evaluation workflow for investigating how well assistant responses align with references and retrieved evidence.

The golden dataset includes realistic owner questions covering multiple business scenarios.

---

## Future Improvements

Potential enhancements include:

- More targeted MCP retrieval and result filtering.
- Improved evaluation coverage for ambiguous conversations.
- Automated regression testing for tool calls.
- Factual-correctness and safety-specific evaluation.
- Production deployment with managed PostgreSQL.
- Additional monitoring and alerting.
- Historical business trends and forecasting.

---

## Project Status

**Functional portfolio prototype**

Implemented capabilities include:

- Multi-branch PostgreSQL connectivity.
- Custom FastMCP tools.
- LangGraph-based conversational workflow.
- Owner and manager authentication.
- Role-based business data access.
- Business analytics dashboard.
- Ragas evaluation pipeline.
- Langfuse observability integration.

This project is intended to demonstrate applied AI engineering, tool integration, backend development, database design, evaluation, and secure AI application architecture.

---

## Disclaimer

StoreBridge MCP is an independent educational and portfolio project inspired by practical retail operations.

Walk & Talk is used as the fictionalized demonstration business context. The application does not use actual company transaction data, employee records, or confidential business information.

All provided business datasets are synthetic.

---

## Author

**Mohamed Akshan**

Data Science Undergraduate | AI/ML Engineering

[Portfolio](https://mohamed-akshan-portfolio.vercel.app/)
