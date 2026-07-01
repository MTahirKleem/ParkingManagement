# Phase 8 Parking Module Design

## Scope

Implement the Phase 8 prompt exactly: vehicle entry and exit, active/history/search/detail reads, Admin-only correction and soft deletion, fixed/hourly fee calculation, embedded cash payment and pricing snapshots, parking audit actions, and idempotent pricing seeding.

Authentication, user management, dashboards, reports, exports, OCR, frontend work, online payments, tenancy, branches, and new collections remain out of scope.

## Architecture

The module extends the existing async layers:

```text
parking router -> ParkingService -> ParkingRepository -> MongoDB
                         |
                         +-> PricingService -> PricingRepository
                         +-> AuditLogService
```

Routers own HTTP parsing and standard response envelopes. Services enforce lifecycle, authorization-independent business rules, normalization, fee calculation, payment/snapshot construction, and audits. Repositories contain only Motor queries and atomic writes.

## Parking Lifecycle

Entry normalizes the displayed plate, checks for an active duplicate, and inserts the complete active-record shape. The existing partial unique index remains the final concurrency guard; duplicate-key races map to `409 DUPLICATE_ACTIVE_VEHICLE`.

Exit validates the ObjectId and record state, requires confirmed cash receipt, asks `PricingService` for fee data, then atomically changes only an active record to completed. A concurrent or repeated exit is reclassified as `409 VEHICLE_ALREADY_COMPLETED`. The payment and pricing snapshot are embedded in the same parking document.

Duration uses `ceil(total_seconds / 60)` with a minimum of zero. Fixed pricing returns the fixed rate. Hourly pricing subtracts grace without going below zero, rounds hours upward, charges at least `base_fee`, and adds `extra_hour_fee` beyond `base_hours`.

## Queries and Updates

Active listing always forces `status=active`, supports normalized partial plate search and vehicle type, and sorts newest entry first.

History excludes deleted records by default. A completed status filter applies date bounds to `exit_time`; active applies them to `entry_time`; an unfiltered history date range matches completed records by exit time and other records by entry time. End dates are inclusive through the next UTC midnight. Completed history sorts by exit time; other history sorts by creation time.

Search performs exact normalized-plate matching and excludes deleted records. Details also hide deleted records.

Admin updates permit only plate number, vehicle type, slot, and notes. Plate changes are renormalized, and active records retain duplicate protection. Deletion is an atomic soft delete with actor and UTC update metadata.

## Validation, Errors, and Responses

Pydantic v2 schemas forbid undeclared mutation fields. Entry requires a non-empty plate and valid vehicle type. Exit accepts only `payment_received=true`. Query schemas enforce allowed enums, dates, and pagination limits.

Errors use the Phase 7 envelope and the Phase 8 codes:

- `400 VALIDATION_ERROR`
- `404 PARKING_RECORD_NOT_FOUND`
- `404 PRICING_RULE_NOT_FOUND`
- `409 DUPLICATE_ACTIVE_VEHICLE`
- `409 VEHICLE_ALREADY_COMPLETED`
- existing authentication and authorization codes

ObjectIds are serialized to strings. No user password data is joined or exposed.

## Verification

Tests cover normalization, schema validation, fixed/hourly/grace pricing, repository query construction, duplicate races, all lifecycle transitions, audits, RBAC, route contracts, seed idempotency, and Phase 7 regression. Live MongoDB verification seeds pricing and exercises Admin and Guard Swagger-equivalent flows while cleaning verification records afterward.
