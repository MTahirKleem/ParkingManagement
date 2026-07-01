# Phase 7 Authentication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the complete Phase 7 FastAPI authentication and Admin-only Guard-management backend defined by the approved prompt.

**Architecture:** Keep routers thin, business rules in async services, and Motor queries in repositories. Shared Pydantic schemas, security/permission dependencies, serializers, constants, and error handlers provide the public contract.

**Tech Stack:** Python 3.13+, FastAPI, Pydantic v2, Motor/PyMongo, Passlib bcrypt, python-jose, pytest

---

### Task 1: Foundations

**Files:**
- Create: `backend/tests/test_security_and_utils.py`
- Modify: `backend/app/core/constants.py`
- Modify: `backend/app/core/security.py`
- Modify: `backend/app/utils/object_id.py`
- Modify: `backend/app/utils/datetime.py`

- [ ] Write tests asserting bcrypt round trips, JWT claims/expiry decoding, UTC-aware timestamps, valid/invalid ObjectId handling, and recursive `_id` serialization.
- [ ] Run `python -m pytest tests/test_security_and_utils.py -v` from `backend`; expect failures because helpers are absent.
- [ ] Implement exactly the constants and helper functions required by the prompt.
- [ ] Re-run the focused test; expect all tests to pass.

### Task 2: Models, Schemas, and Errors

**Files:**
- Create: `backend/tests/test_schemas.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/audit_log.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/common.py`
- Modify: `backend/app/middleware/error_handler.py`
- Modify: `backend/app/main.py`

- [ ] Write tests for valid payloads, invalid email, short password, non-Guard creation, forbidden update fields, pagination shape, and standardized application/validation errors.
- [ ] Run `python -m pytest tests/test_schemas.py -v`; expect import/validation failures.
- [ ] Implement strict Pydantic v2 request/response models and registered FastAPI error handlers.
- [ ] Re-run the focused test; expect all tests to pass.

### Task 3: Repositories and Audit Service

**Files:**
- Create: `backend/tests/test_repositories.py`
- Create: `backend/app/repositories/user_repository.py`
- Create: `backend/app/repositories/audit_log_repository.py`
- Create: `backend/app/services/audit_log_service.py`

- [ ] Write async tests using collection doubles to assert each required repository query/update, escaped search filters, pagination, and append-only audit creation.
- [ ] Run `python -m pytest tests/test_repositories.py -v`; expect missing-module failures.
- [ ] Implement every repository method named in the prompt and safe audit-context extraction.
- [ ] Re-run the focused test; expect all tests to pass.

### Task 4: Authentication and Permissions

**Files:**
- Create: `backend/tests/test_auth_service.py`
- Create: `backend/tests/test_permissions.py`
- Create: `backend/app/services/auth_service.py`
- Modify: `backend/app/core/permissions.py`

- [ ] Write async tests for valid login, invalid credentials, inactive/deleted users, last-login update, safe success/failure audits, missing/invalid/expired tokens, missing users, inactive users, Admin access, and Guard denial.
- [ ] Run the two focused test files; expect missing behavior failures.
- [ ] Implement `AuthService`, `get_current_user`, `require_roles`, and `require_admin`.
- [ ] Re-run the focused tests; expect all tests to pass.

### Task 5: Guard Management Service

**Files:**
- Create: `backend/tests/test_user_service.py`
- Create: `backend/app/services/user_service.py`

- [ ] Write async tests for create/list/get/update/soft-delete/reset, duplicate email, invalid IDs, missing users, self-delete denial, hashing, safe output, and required audit actions.
- [ ] Run `python -m pytest tests/test_user_service.py -v`; expect missing-module failures.
- [ ] Implement the prompt's complete `UserService` API and business rules.
- [ ] Re-run the focused test; expect all tests to pass.

### Task 6: HTTP Routes and Stateless Refresh

**Files:**
- Create: `backend/tests/test_api_routes.py`
- Create: `backend/app/api/v1/auth.py`
- Create: `backend/app/api/v1/users.py`
- Modify: `backend/app/api/v1/router.py`

- [ ] Write API tests asserting all required paths/methods, response envelopes, request context forwarding, Admin dependencies, password secrecy, and refresh issuing a fresh token from an active Bearer-authenticated user.
- [ ] Run `python -m pytest tests/test_api_routes.py -v`; expect missing-route failures.
- [ ] Implement the auth/users routers and include them without changing health behavior.
- [ ] Re-run the focused test; expect all tests to pass.

### Task 7: Admin Seed and Final Verification

**Files:**
- Create: `backend/tests/test_seed_admin.py`
- Create: `backend/scripts/seed_admin.py`

- [ ] Write an async idempotency test asserting existing admin is preserved and a missing admin is inserted with a bcrypt hash and required document fields.
- [ ] Run `python -m pytest tests/test_seed_admin.py -v`; expect a missing-module failure.
- [ ] Implement the backend-folder runnable seed script using existing configuration.
- [ ] Re-run the focused test; expect all tests to pass.
- [ ] Run `python -m pytest -v`; expect the complete suite to pass.
- [ ] Import `app.main:app`, inspect OpenAPI, and verify every Phase 7 route plus both health routes exists.
- [ ] If local MongoDB responds, run the seed script and exercise the documented login/refresh/me/Guard lifecycle; otherwise report live-database verification as the only environmental limitation.
