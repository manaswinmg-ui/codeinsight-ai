# Local Setup Instructions

This document guides you through setting up and running CodeInsight AI on your local machine.

## Prerequisites
* **Python**: 3.12 or newer
* **Node.js**: 20.x or newer (with npm)
* **Docker & Docker Compose** (optional, but recommended)

---

## 1. Setup Backend Locally
Navigate to the backend directory:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Verify backend tests pass:
```bash
pytest
```

Run local API server:
```bash
uvicorn app.main:app --reload
```
The API is now running at `http://localhost:8000`.

---

## 2. Setup Frontend Locally
Navigate to the frontend directory:
```bash
cd ../frontend
```

Install dependencies:
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```
The web app is now running at `http://localhost:5173`.

---

## 3. Setup with Docker Compose (Recommended)
You can run the database, backend, and frontend concurrently using Docker Compose:

From the root directory:
```bash
docker compose up --build
```
This builds and starts:
* PostgreSQL on `localhost:5432`
* Backend API on `localhost:8000`
* Frontend App on `localhost:5173` (mapped from Nginx port 80)
