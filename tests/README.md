# CodeInsight AI Monorepo Testing

This folder contains monorepo-level integration or End-to-End (E2E) testing configurations.

## Testing Strategy

### 1. Backend Tests (`/backend/tests`)
* **Unit Tests**: Test utility methods, isolated AI clients, and schema conversions.
* **API Integration Tests**: Uses `httpx.AsyncClient` with custom database overrides to test route validations, HTTP statuses, and CRUD database interaction workflows.
* Run backend tests:
  ```bash
  cd backend
  pytest
  ```

### 2. Frontend Tests (`/frontend/src`)
* React component unit tests (e.g. testing input interactions and view states).
* Type compilation check:
  ```bash
  cd frontend
  npm run build  # runs 'tsc && vite build'
  ```

### 3. E2E Tests (`/tests`)
* For future cross-service testing, playwright/cypress configs can be placed here to test the unified container system in a headless browser environment.
