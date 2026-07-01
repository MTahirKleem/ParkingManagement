# Parking User Names Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show user names instead of raw user IDs in parking details for Admin and Guard.

**Architecture:** Add nullable name fields to the existing parking response without replacing audit IDs. Resolve all referenced users through one batch repository query inside `ParkingService`, then make the frontend prefer the name fields with ID fallback.

**Tech Stack:** FastAPI, Pydantic, Motor/MongoDB, pytest, Next.js, TypeScript, Vitest

---

### Task 1: Batch user-name lookup

**Files:**
- Modify: `backend/app/repositories/user_repository.py`
- Test: `backend/tests/test_repositories.py`

- [x] **Step 1: Write the failing repository test**

Add a test that calls `find_names_by_ids` with two valid string IDs and asserts the collection receives one `$in` query with `_id` and `name` projection and returns an ID-to-name mapping.

- [x] **Step 2: Verify the repository test fails**

Run: `pytest tests/test_repositories.py -q`

Expected: failure because `UserRepository.find_names_by_ids` does not exist.

- [x] **Step 3: Implement the batch lookup**

Convert valid IDs to `ObjectId`, query once with `{"_id": {"$in": ids}}`, project `{"name": 1}`, and return `{str(_id): name}`. Return an empty mapping for an empty set.

- [x] **Step 4: Verify the repository test passes**

Run: `pytest tests/test_repositories.py -q`

Expected: all repository tests pass.

### Task 2: Enrich parking responses

**Files:**
- Modify: `backend/app/schemas/parking.py`
- Modify: `backend/app/services/parking_service.py`
- Test: `backend/tests/test_parking_service.py`
- Test: `backend/tests/test_parking_api.py`

- [x] **Step 1: Write failing service and schema tests**

Inject a mocked user repository, return names for creator and payment receiver IDs, and assert detail/list results contain `created_by_name`, `completed_by_name`, and `payment.received_by_name`. Assert unresolved users produce null name fields.

- [x] **Step 2: Verify the parking tests fail**

Run: `pytest tests/test_parking_service.py tests/test_parking_api.py -q`

Expected: failures because the schema and service do not expose name fields.

- [x] **Step 3: Implement response enrichment**

Add nullable fields to Pydantic responses. Inject `UserRepository` into `ParkingService`, serialize records, collect referenced IDs, resolve names once, and attach name fields before returning create, exit, active, history, search, detail, and update responses.

- [x] **Step 4: Verify parking tests pass**

Run: `pytest tests/test_parking_service.py tests/test_parking_api.py -q`

Expected: all parking tests pass.

### Task 3: Render names in parking details

**Files:**
- Modify: `frontend/types/parking.ts`
- Modify: `frontend/components/parking/ParkingRecordDetails.tsx`
- Test: `frontend/tests/parking-forms.test.ts`

- [x] **Step 1: Write the failing frontend test**

Extract and test a `displayUserName(name, id)` helper that returns the name when present and falls back to the ID when the name is null.

- [x] **Step 2: Verify the frontend test fails**

Run: `npm test -- --run tests/parking-forms.test.ts`

Expected: failure because `displayUserName` does not exist.

- [x] **Step 3: Implement frontend name display**

Add optional name fields to parking types, implement the display helper, and use it for Created by, Completed by, and Received by without monospace styling when a name exists.

- [x] **Step 4: Verify frontend checks**

Run: `npm test -- --run && npx tsc --noEmit && npm run lint && npm run build`

Expected: all tests, type checking, lint, and production build pass.

### Task 4: Full verification and commit

**Files:**
- Verify all files above

- [x] **Step 1: Run backend verification**

Run: `pytest -q` from `backend`

Expected: all backend tests pass.

- [x] **Step 2: Run frontend verification**

Run: `npm test -- --run && npx tsc --noEmit && npm run lint && npm run build` from `frontend`

Expected: all frontend checks pass.

- [x] **Step 3: Commit**

Run:

```bash
git add backend frontend docs/superpowers
git commit -m "feat: show user names in parking details"
```
