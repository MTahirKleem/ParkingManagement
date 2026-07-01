# Phase 7 Authentication Design

## Scope

Implement only the authentication and user-access foundation defined by the Phase 7 prompt: JWT authentication, current-user lookup, stateless token refresh, Admin/Guard authorization, admin-only Guard management, audit logging, and idempotent default-admin seeding.

No parking, pricing, dashboard, reporting, OCR, frontend, tenancy, or long-lived refresh-token functionality is included.

## Architecture

The existing async layered architecture remains:

```text
FastAPI router -> service -> repository -> MongoDB
```

Routers handle HTTP concerns and request context. Services enforce authentication and user-management rules. Repositories contain Motor queries. Pydantic v2 schemas validate all API input and shape all output. Shared security, permission, ObjectId, datetime, constant, response, and error helpers keep cross-cutting behavior consistent.

Only the existing `users` and `audit_logs` collections are used.

## Authentication

- Passwords use Passlib bcrypt hashing.
- Access tokens use `python-jose`, the configured secret/algorithm, UTC expiry, and `sub` plus `role` claims.
- Login accepts normalized email and password, rejects missing/incorrect credentials with `401 INVALID_CREDENTIALS`, and rejects inactive/deleted accounts with `403 USER_INACTIVE`.
- Successful login updates `last_login_at`, writes `USER_LOGIN`, and returns the token plus a password-free user summary.
- Failed login writes `USER_LOGIN_FAILED` without recording password, hash, or token. When no account exists, actor fields are null and the attempted email is safe metadata.
- `get_current_user` validates Bearer authentication, distinguishes missing, expired, and invalid tokens, reloads the user, and requires active status.
- `/auth/refresh` uses the same current-token authentication path and issues a fresh access token. It creates no refresh-token collection or persistent refresh-token state.

## User Management

All `/users` routes require the Admin role. The create endpoint accepts only `guard`; list supports pagination, role/status filters, and escaped case-insensitive name/email search; get/update/delete/reset validate ObjectIds before querying.

Updates permit only name, phone, and status. Delete is a soft delete and cannot target the authenticated admin. Password reset uses the dedicated endpoint. Every mutation records the acting admin in `created_by` or `updated_by` and appends the required audit action.

## Data and Responses

User documents follow `docs/database.md`. API serialization converts `_id` to string `id`, recursively stringifies ObjectIds, and never returns `password_hash`. Datetimes are timezone-aware UTC at application boundaries.

Success and paginated responses follow `docs/api.md`. Application errors use:

```json
{
  "success": false,
  "message": "Human-readable message",
  "error_code": "DOCUMENTED_CODE",
  "details": {}
}
```

The application registers handlers for domain errors, FastAPI validation errors, and unhandled errors.

## Verification

Automated tests cover security helpers, ObjectId serialization, request validation, login outcomes and audit behavior, token/current-user permissions, stateless refresh, Guard CRUD rules, pagination, soft deletion, password reset, response secrecy, routes, and seed idempotency. Final verification runs the complete pytest suite, imports the app, checks the OpenAPI route set, and runs live MongoDB/Swagger checks when MongoDB is available.
