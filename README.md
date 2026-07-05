# CodeInsight AI

CodeInsight AI is a production-grade, AI-powered code review platform. This repository is structured as a monorepo containing a Python (FastAPI) backend, React (Vite + TypeScript) frontend, and multi-container Docker deployment configs.

---

## Repository Structure

```
codeinsight-ai/
├── README.md                 # Master setup & development guide
├── docker-compose.yml        # Multi-container local orchestration
├── .gitignore                # Global git ignore configurations
├── .github/
│   └── workflows/
│       └── ci.yml            # CI validation pipeline (lints & tests)
├── docker/
│   └── postgres/
│       └── init.sql          # DB engine initialization script
├── docs/
│   ├── architecture.md       # Layered architecture documentation
│   └── setup.md              # Detailed local machine setup
├── tests/
│   └── README.md             # Multi-tier testing strategy guide
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml        # Ruff, Black, and Pytest configuration
│   ├── requirements.txt      # Backend library dependencies
│   ├── alembic.ini           # Alembic migration configuration
│   ├── .env.example          # Template environment configurations
│   ├── app/                  # FastAPI Application Package
│   │   ├── main.py           # API Server Entry point
│   │   ├── api/              # Controllers & Routers Layer
│   │   ├── services/         # Core Business Logic Layer
│   │   ├── repositories/     # Data Access Layer (CRUD)
│   │   ├── models/           # SQLAlchemy DB Models Mapping
│   │   ├── schemas/          # Pydantic Schema Serialization/Validation
│   │   ├── config/           # Pydantic Settings Validation
│   │   ├── ai/               # AI LLM Provider Integrations
│   │   ├── middleware/       # CORS & Custom Logging Middlewares
│   │   └── utils/            # Shared Stateless Helper Utilities
│   └── tests/                # Pytest suites
└── frontend/
    ├── Dockerfile
    ├── package.json          # Node package definition
    ├── tsconfig.json         # TS Compiler options
    ├── vite.config.ts        # Vite build & proxy settings
    ├── .eslintrc.cjs         # ESLint 8.x linting guidelines
    ├── .prettierrc           # Prettier configuration rules
    ├── index.html            # Static entrypoint page
    ├── .env.example          # Frontend configuration variables
    └── src/                  # React Source Code
        ├── main.tsx          # DOM root mount
        ├── App.tsx           # Dashboard / Shell view
        ├── index.css         # Glassmorphic UI CSS styling tokens
        ├── components/       # Shared UI components
        ├── pages/            # View pages
        └── services/         # API connection handlers
```

---

## Getting Started

### 1. Docker Compose (Recommended)
Build and start the PostgreSQL database, FastAPI backend, and React frontend containers concurrently:
```bash
docker compose up --build
```
* **Frontend**: `http://localhost:5173`
* **Backend API**: `http://localhost:8000`
* **API Documentation**: `http://localhost:8000/docs`
* **PostgreSQL**: `localhost:5432`

### 2. Manual Development Setup
For detailed setup instructions on your local environment (virtual environments, npm configurations), refer to [docs/setup.md](file:///c:/Users/manas/OneDrive/Desktop/SDE/Antigravity_projects/codeinsight-ai/docs/setup.md).

---

## Development Workflow

### Backend

1. **Active Environment**:
   Always run commands inside your virtual environment:
   ```bash
   cd backend
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. **Linting**:
   Ruff is used to analyze static code quality:
   ```bash
   ruff check .
   ruff check . --fix  # Auto-fix fixable violations
   ```
3. **Formatting**:
   Black is the standard formatter:
   ```bash
   black .
   ```
4. **Testing**:
   Run the pytest suites:
   ```bash
   pytest
   ```

### Frontend

1. **Active Environment**:
   ```bash
   cd frontend
   ```
2. **Linting**:
   ```bash
   npm run lint
   ```
3. **Formatting**:
   Prettier is used for styling formatting:
   ```bash
   npm run format
   ```
4. **Build Verification**:
   Verify compilation and bundler assets:
   ```bash
   npm run build
   ```

---

## Coding Standards

### Backend Guidelines
* **Type Annotations**: All function signatures must include strict type annotations for arguments and return types.
* **SQLAlchemy 2.0 Style**: Use `select()` statements and mappings with `Mapped[]` and `mapped_column()` syntax.
* **Database Access**: Never query the database directly in controllers or services; database reads and writes must be isolated inside the `repositories/` package.
* **Configurations**: Never read raw OS environment variables; use Pydantic validation inside `app/config/settings.py`.

### Frontend Guidelines
* **TypeScript**: Avoid using `any`; define interfaces or types for all data models.
* **Styling**: Make use of CSS Custom Properties defined in `src/index.css` to build beautiful glassmorphic visual pages.
* **React Hooks**: Follow React Hook rules (checked via ESLint). Implement custom hooks to decouple UI rendering from data fetching.
