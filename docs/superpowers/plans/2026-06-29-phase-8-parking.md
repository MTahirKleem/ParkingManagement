# Phase 8 Parking Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the complete Phase 8 parking lifecycle and pricing calculation backend without expanding MVP scope.

**Architecture:** Extend the Phase 7 FastAPI router/service/repository structure. ParkingService orchestrates lifecycle and auditing, PricingService owns fee calculation, and repositories provide isolated Motor queries and atomic updates.

**Tech Stack:** Python, FastAPI, Pydantic v2, Motor/PyMongo, MongoDB, pytest

---

### Task 1: Parking and Pricing Foundations

**Files:**
- Create: `backend/tests/test_parking_foundations.py`
- Create: `backend/app/utils/plate.py`
- Create: `backend/app/models/parking_record.py`
- Create: `backend/app/models/pricing_rule.py`
- Create: `backend/app/schemas/parking.py`
- Create: `backend/app/schemas/pricing.py`
- Modify: `backend/app/core/constants.py`

- [ ] Write failing tests for all normalization examples, enum constants, entry/exit/update validation, query pagination/status/date validation, and response ObjectId shapes.
- [ ] Run `python -m pytest tests/test_parking_foundations.py -q`; expect missing-module failures.
- [ ] Implement the required constants, models, schemas, and normalization utility with undeclared mutation fields forbidden.
- [ ] Re-run the focused tests; expect all tests to pass.

### Task 2: Pricing Repository and Fee Calculation

**Files:**
- Create: `backend/tests/test_pricing.py`
- Create: `backend/app/repositories/pricing_repository.py`
- Create: `backend/app/services/pricing_service.py`

- [ ] Write failing async tests for active pricing lookup, creation/read methods, missing-rule errors, fixed fees, hourly base fees, grace behavior, and rounded extra hours.
- [ ] Run `python -m pytest tests/test_pricing.py -q`; expect missing-module failures.
- [ ] Implement the three required repository methods and both required service methods.
- [ ] Re-run the focused tests; expect all tests to pass.

### Task 3: Parking Repository

**Files:**
- Create: `backend/tests/test_parking_repository.py`
- Create: `backend/app/repositories/parking_repository.py`

- [ ] Write failing async tests for all required repository methods, ObjectId conversion, duplicate exclusion, active filters, history date-field behavior, deleted exclusion, exact search, atomic completion, and soft deletion.
- [ ] Run `python -m pytest tests/test_parking_repository.py -q`; expect a missing-module failure.
- [ ] Implement Motor-only query and write behavior, with no pricing, role, or audit rules.
- [ ] Re-run the focused tests; expect all tests to pass.

### Task 4: Parking Service

**Files:**
- Create: `backend/tests/test_parking_service.py`
- Create: `backend/app/services/parking_service.py`
- Modify: `backend/app/core/constants.py`

- [ ] Write failing async tests for entry creation/duplicate handling, exit states/payment/pricing embedding, active/history/search/detail reads, invalid IDs, Admin updates, active duplicate updates, soft deletion, and all four parking audit actions.
- [ ] Run `python -m pytest tests/test_parking_service.py -q`; expect a missing-module failure.
- [ ] Implement every ParkingService method required by the prompt and add parking audit/error constants.
- [ ] Re-run the focused tests; expect all tests to pass.

### Task 5: Parking HTTP API and RBAC

**Files:**
- Create: `backend/tests/test_parking_api.py`
- Create: `backend/app/api/v1/parking.py`
- Modify: `backend/app/api/v1/router.py`

- [ ] Write failing API tests for all eight routes, standard envelopes, query validation, Admin/Guard shared access, Guard update/delete denial, missing token errors, and unchanged Phase 7/OpenAPI routes.
- [ ] Run `python -m pytest tests/test_parking_api.py -q`; expect missing routes.
- [ ] Implement thin parking routes using existing `get_current_user`, `require_roles`, and `require_admin`, then include the router.
- [ ] Re-run the focused tests; expect all tests to pass.

### Task 6: Pricing Seed and Complete Verification

**Files:**
- Create: `backend/tests/test_seed_pricing.py`
- Create: `backend/scripts/seed_pricing.py`

- [ ] Write failing tests proving bike/car defaults, idempotency, UTC metadata, and clear output.
- [ ] Run `python -m pytest tests/test_seed_pricing.py -q`; expect a missing-module failure.
- [ ] Implement the backend-folder runnable seed script using existing MongoDB configuration.
- [ ] Run the focused seed tests and then `python -m pytest -q`; expect the complete Phase 7+8 suite to pass.
- [ ] Run `python -m compileall -q app scripts`, `git diff --check`, and inspect OpenAPI for every required route.
- [ ] With local MongoDB, seed pricing and execute entry, duplicate, reads, fixed/hourly exit, repeat-exit, Admin update/delete, Guard create/exit/RBAC, audit, and Phase 7 regression checks.
