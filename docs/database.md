
# Phase 3 – ParkingManagement Database Design

## 1. Phase Goal

The goal of this phase is to finalize the MongoDB database design before writing backend code.

This phase defines:

* Database name
* Collections
* Field structure
* Embedded objects
* Enum values
* Indexes
* Seed data
* Business rules
* Future expansion points

No FastAPI code should be written in this phase.

The output of this phase will guide:

* Pydantic models
* Request schemas
* Response schemas
* Repository methods
* Service logic
* Dashboard queries
* Report queries

## 2. Database Name

The development database name is:

```text
parkingmanagement
```

MongoDB connection URI for local development:

```text
mongodb://localhost:27017
```

Full development database connection:

```text
mongodb://localhost:27017/parkingmanagement
```

## 3. MVP Collections

ParkingManagement MVP will use only these collections:

```text
users
parking_records
pricing_rules
settings
audit_logs
```

## 4. Collections Not Included in MVP

The following collections are intentionally not included in Version 1:

```text
payments
parking_slots
malls
operators
tenants
subscriptions
branches
devices
```

Reason:

* Payment data is stored inside `parking_records`.
* Parking slot is stored as optional text inside `parking_records`.
* Multi-tenant SaaS collections can be added later.
* MVP should stay simple and complete the core parking workflow first.

## 5. Collection Purpose

| Collection      | Purpose                                                   |
| --------------- | --------------------------------------------------------- |
| users           | Stores Admin and Guard accounts                           |
| parking_records | Stores vehicle entry, exit, fee, payment, OCR, and status |
| pricing_rules   | Stores bike and car pricing rules                         |
| settings        | Stores parking business configuration                     |
| audit_logs      | Stores important system actions                           |

## 6. Enum Values

### User Roles

```text
admin
guard
```

### User Status

```text
active
inactive
deleted
```

### Vehicle Types

```text
bike
car
```

### Parking Status

```text
active
completed
cancelled
deleted
```

### Payment Method

```text
cash
```

### Pricing Type

```text
fixed
hourly
```

### Currency

```text
PKR
```

## 7. users Collection

The `users` collection stores Admin and Guard accounts.

### Document Shape

```json
{
  "_id": "ObjectId",
  "name": "Ali Guard",
  "email": "guard@parkingmanagement.com",
  "phone": "+923001234567",
  "password_hash": "hashed_password",
  "role": "guard",
  "status": "active",
  "last_login_at": null,
  "created_by": "ObjectId",
  "updated_by": "ObjectId",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Required Fields

```text
name
email
password_hash
role
status
created_at
updated_at
```

### Optional Fields

```text
phone
last_login_at
created_by
updated_by
```

### Business Rules

* Email must be unique.
* Password must be hashed.
* Password must never be returned in API responses.
* Admin can create Guard users.
* Guard cannot create users.
* Deleted users are soft deleted with `status = deleted`.
* Inactive and deleted users cannot log in.
* Admin account should be created through seed data.

### Indexes

```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ role: 1 })
db.users.createIndex({ status: 1 })
db.users.createIndex({ created_at: -1 })
```

## 8. parking_records Collection

The `parking_records` collection is the main collection.

It stores the full parking lifecycle:

```text
Entry → Active → Exit → Fee Calculation → Cash Payment → Completed
```

### Active Parking Record Shape

```json
{
  "_id": "ObjectId",
  "plate_number": "LEA-1234",
  "normalized_plate_number": "LEA1234",
  "vehicle_type": "bike",
  "slot": "A-12",
  "entry_time": "2026-06-29T10:00:00Z",
  "exit_time": null,
  "status": "active",
  "duration_minutes": null,
  "fee": null,
  "currency": "PKR",
  "payment": null,
  "pricing_snapshot": null,
  "ocr": null,
  "notes": null,
  "created_by": "ObjectId",
  "completed_by": null,
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Completed Parking Record Shape

```json
{
  "_id": "ObjectId",
  "plate_number": "LEA-1234",
  "normalized_plate_number": "LEA1234",
  "vehicle_type": "bike",
  "slot": "A-12",
  "entry_time": "2026-06-29T10:00:00Z",
  "exit_time": "2026-06-29T12:15:00Z",
  "status": "completed",
  "duration_minutes": 135,
  "fee": 50,
  "currency": "PKR",
  "payment": {
    "method": "cash",
    "received": true,
    "received_by": "ObjectId",
    "received_at": "2026-06-29T12:16:00Z"
  },
  "pricing_snapshot": {
    "pricing_rule_id": "ObjectId",
    "pricing_type": "fixed",
    "fixed_rate": 50,
    "base_hours": null,
    "base_fee": null,
    "extra_hour_fee": null,
    "grace_minutes": 0
  },
  "ocr": null,
  "notes": null,
  "created_by": "ObjectId",
  "completed_by": "ObjectId",
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T12:16:00Z"
}
```

### Required Fields on Entry

```text
plate_number
normalized_plate_number
vehicle_type
entry_time
status
currency
created_by
created_at
updated_at
```

### Required Fields on Exit

```text
exit_time
duration_minutes
fee
payment
pricing_snapshot
completed_by
updated_at
```

### Optional Fields

```text
slot
ocr
notes
updated_by
```

### Business Rules

* Plate number is required.
* Vehicle type is required.
* Vehicle type must be `bike` or `car`.
* Entry time is automatic.
* Exit time is automatic.
* Status starts as `active`.
* Status becomes `completed` after exit.
* Same active plate number cannot exist twice.
* Fee is calculated only during exit.
* Payment method is cash only.
* Payment is embedded inside parking record.
* Pricing snapshot is embedded inside completed parking record.
* Completed record cannot be exited again.
* Deleted records should not appear in reports.
* Admin edits must create audit logs.

### Indexes

```javascript
db.parking_records.createIndex({ normalized_plate_number: 1 })
db.parking_records.createIndex({ status: 1 })
db.parking_records.createIndex({ vehicle_type: 1 })
db.parking_records.createIndex({ entry_time: -1 })
db.parking_records.createIndex({ exit_time: -1 })
db.parking_records.createIndex({ created_by: 1 })
db.parking_records.createIndex({ completed_by: 1 })
db.parking_records.createIndex({ "payment.received": 1 })
```

### Partial Unique Index for Active Vehicles

Only one active vehicle with the same normalized plate number should be allowed.

```javascript
db.parking_records.createIndex(
  { normalized_plate_number: 1, status: 1 },
  {
    unique: true,
    partialFilterExpression: { status: "active" }
  }
)
```

## 9. Embedded Payment Object

Payment is not a separate collection.

It is stored inside `parking_records`.

### Shape

```json
{
  "method": "cash",
  "received": true,
  "received_by": "ObjectId",
  "received_at": "2026-06-29T12:16:00Z"
}
```

### Business Rules

* Payment is created only during vehicle exit.
* Method is always `cash` in MVP.
* `received` must be `true` before completing parking session.
* Revenue reports count only records where `payment.received = true`.

## 10. Embedded Pricing Snapshot Object

Pricing snapshot is stored inside completed parking records.

### Shape

```json
{
  "pricing_rule_id": "ObjectId",
  "pricing_type": "hourly",
  "fixed_rate": null,
  "base_hours": 2,
  "base_fee": 100,
  "extra_hour_fee": 50,
  "grace_minutes": 10
}
```

### Why Pricing Snapshot Is Required

Pricing can change later.

Old completed records should keep the original fee calculation.

Example:

```text
Today car fee = PKR 100
Tomorrow car fee = PKR 150
Yesterday's completed records must still show PKR 100
```

So the pricing used at the time of exit must be stored inside the parking record.

## 11. Embedded OCR Object

OCR is optional and future-ready.

### Shape

```json
{
  "used": true,
  "plate": "LEA-1234",
  "confidence": 0.95,
  "image_url": "uploads/plates/record_001.jpg"
}
```

### Business Rules

* OCR is optional.
* Manual entry must always be available.
* OCR should not automatically create parking entry.
* Guard must confirm or correct OCR result before saving.
* If OCR is not used, `ocr` can be `null`.

## 12. pricing_rules Collection

The `pricing_rules` collection stores active pricing for bike and car.

MVP supports two pricing modes:

```text
fixed
hourly
```

### Fixed Pricing Shape

```json
{
  "_id": "ObjectId",
  "vehicle_type": "bike",
  "pricing_type": "fixed",
  "fixed_rate": 50,
  "base_hours": null,
  "base_fee": null,
  "extra_hour_fee": null,
  "grace_minutes": 0,
  "currency": "PKR",
  "is_active": true,
  "created_by": "ObjectId",
  "updated_by": "ObjectId",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Hourly Pricing Shape

```json
{
  "_id": "ObjectId",
  "vehicle_type": "car",
  "pricing_type": "hourly",
  "fixed_rate": null,
  "base_hours": 2,
  "base_fee": 100,
  "extra_hour_fee": 50,
  "grace_minutes": 10,
  "currency": "PKR",
  "is_active": true,
  "created_by": "ObjectId",
  "updated_by": "ObjectId",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Required Fields

```text
vehicle_type
pricing_type
currency
is_active
created_at
updated_at
```

### Conditional Fields

For fixed pricing:

```text
fixed_rate
```

For hourly pricing:

```text
base_hours
base_fee
extra_hour_fee
```

### Business Rules

* Only Admin can update pricing.
* Vehicle type must be `bike` or `car`.
* Pricing type must be `fixed` or `hourly`.
* Fixed pricing requires `fixed_rate`.
* Hourly pricing requires `base_hours`, `base_fee`, and `extra_hour_fee`.
* Each vehicle type should have one active pricing rule.
* Pricing changes affect future exits only.
* Completed records keep their old fee through pricing snapshot.

### Indexes

```javascript
db.pricing_rules.createIndex({ vehicle_type: 1 })
db.pricing_rules.createIndex({ is_active: 1 })
db.pricing_rules.createIndex({ vehicle_type: 1, is_active: 1 })
```

## 13. settings Collection

The `settings` collection stores business-level configuration.

For MVP, there should be one settings document.

### Shape

```json
{
  "_id": "ObjectId",
  "parking_name": "ParkingManagement",
  "address": "Lahore, Pakistan",
  "phone": "+923001234567",
  "currency": "PKR",
  "logo_url": null,
  "receipt_footer": "Thank you for parking with us.",
  "parking_capacity": 100,
  "timezone": "Asia/Karachi",
  "created_by": "ObjectId",
  "updated_by": "ObjectId",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Business Rules

* Only Admin can update settings.
* Settings should be created during initial setup.
* Currency defaults to `PKR`.
* Timezone defaults to `Asia/Karachi`.
* Parking capacity is used for occupancy calculation.
* Settings changes must create audit logs.

### Indexes

```javascript
db.settings.createIndex({ parking_name: 1 })
```

## 14. audit_logs Collection

The `audit_logs` collection stores important actions.

### Shape

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "user_role": "guard",
  "action": "VEHICLE_ENTRY_CREATED",
  "entity": "parking_record",
  "entity_id": "ObjectId",
  "message": "Vehicle entry created for LEA-1234",
  "metadata": {
    "plate_number": "LEA-1234",
    "vehicle_type": "bike"
  },
  "ip_address": "127.0.0.1",
  "user_agent": "Mozilla/5.0",
  "created_at": "2026-06-29T10:00:00Z"
}
```

### Audit Actions

```text
USER_LOGIN
USER_LOGIN_FAILED
USER_CREATED
USER_UPDATED
USER_DELETED
USER_PASSWORD_RESET

VEHICLE_ENTRY_CREATED
VEHICLE_EXIT_COMPLETED
PARKING_RECORD_UPDATED
PARKING_RECORD_DELETED
PARKING_RECORD_CANCELLED

PRICING_RULE_CREATED
PRICING_RULE_UPDATED

SETTINGS_UPDATED

REPORT_GENERATED
EXPORT_PDF_GENERATED
EXPORT_EXCEL_GENERATED
```

### Business Rules

* Audit logs are append-only.
* Audit logs should not be edited from the UI.
* Audit logs should not be deleted from the UI.
* Passwords must never be logged.
* JWT tokens must never be logged.
* Password hashes must never be logged.
* Important Admin actions must always create audit logs.
* Vehicle entry and exit must always create audit logs.

### Indexes

```javascript
db.audit_logs.createIndex({ user_id: 1 })
db.audit_logs.createIndex({ action: 1 })
db.audit_logs.createIndex({ entity: 1, entity_id: 1 })
db.audit_logs.createIndex({ created_at: -1 })
```

## 15. Plate Number Normalization

The system stores both:

```text
plate_number
normalized_plate_number
```

Example:

```text
plate_number = LEA-1234
normalized_plate_number = LEA1234
```

These inputs should all match the same record:

```text
LEA-1234
LEA 1234
lea1234
LEA1234
```

Normalization rules:

* Convert to uppercase.
* Remove spaces.
* Remove hyphens.
* Remove special characters.
* Keep letters and numbers only.

## 16. Date and Time Rules

* Store all datetimes in UTC.
* Convert to local timezone in frontend.
* Default local timezone is `Asia/Karachi`.
* Use `created_at` for document creation.
* Use `updated_at` for document updates.
* Use `entry_time` for vehicle entry.
* Use `exit_time` for vehicle exit.
* Use `payment.received_at` for cash received time.
* Use `exit_time` for revenue reports.

## 17. Report Query Rules

Reports should use `parking_records`.

### Revenue Report Filter

```javascript
{
  status: "completed",
  "payment.received": true
}
```

### Daily Report Filter

```javascript
{
  status: "completed",
  "payment.received": true,
  exit_time: {
    $gte: startOfDay,
    $lte: endOfDay
  }
}
```

### Monthly Report Filter

```javascript
{
  status: "completed",
  "payment.received": true,
  exit_time: {
    $gte: startOfMonth,
    $lte: endOfMonth
  }
}
```

### Revenue by Guard

Group by:

```text
payment.received_by
```

### Revenue by Vehicle Type

Group by:

```text
vehicle_type
```

## 18. Dashboard Query Rules

### Guard Dashboard

Guard dashboard shows:

```text
active_vehicles
today_entries
today_exits
recent_entries
```

Guard dashboard can use:

```javascript
{
  created_by: current_user_id
}
```

for guard-specific data.

### Admin Dashboard

Admin dashboard shows:

```text
total_revenue
today_revenue
monthly_revenue
active_vehicles
completed_vehicles
today_entries
today_exits
parking_occupancy
revenue_by_guard
revenue_by_vehicle_type
recent_transactions
```

Admin dashboard uses all parking records.

## 19. Initial Seed Data

The backend should later include a seed script.

Seed data should create:

```text
Default Admin
Default Bike Pricing
Default Car Pricing
Default Settings
```

### Default Admin

```json
{
  "name": "System Admin",
  "email": "admin@parkingmanagement.com",
  "phone": null,
  "password_hash": "hashed_default_password",
  "role": "admin",
  "status": "active",
  "last_login_at": null,
  "created_by": null,
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Default Bike Pricing

```json
{
  "vehicle_type": "bike",
  "pricing_type": "fixed",
  "fixed_rate": 50,
  "base_hours": null,
  "base_fee": null,
  "extra_hour_fee": null,
  "grace_minutes": 0,
  "currency": "PKR",
  "is_active": true,
  "created_by": null,
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Default Car Pricing

```json
{
  "vehicle_type": "car",
  "pricing_type": "fixed",
  "fixed_rate": 100,
  "base_hours": null,
  "base_fee": null,
  "extra_hour_fee": null,
  "grace_minutes": 0,
  "currency": "PKR",
  "is_active": true,
  "created_by": null,
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Default Settings

```json
{
  "parking_name": "ParkingManagement",
  "address": "Lahore, Pakistan",
  "phone": null,
  "currency": "PKR",
  "logo_url": null,
  "receipt_footer": "Thank you for parking with us.",
  "parking_capacity": 100,
  "timezone": "Asia/Karachi",
  "created_by": null,
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

## 20. Future Expansion

Future SaaS version may add:

```text
tenants
branches
subscriptions
invoices
devices
payment_gateways
parking_slots
```

When multi-tenant SaaS is added, these collections will receive `tenant_id`:

```text
users
parking_records
pricing_rules
settings
audit_logs
```

This is not required in MVP.

## 21. Phase 3 Completion Checklist

Phase 3 is complete when the following are finalized:

```text
Database name finalized
Collections finalized
Fields finalized
Embedded objects finalized
Enum values finalized
Indexes finalized
Seed data finalized
Report query rules finalized
Dashboard query rules finalized
Soft delete rules finalized
Future expansion notes finalized
```

## 22. Final Database Summary

ParkingManagement MVP uses a simple MongoDB database with five collections:

```text
users
parking_records
pricing_rules
settings
audit_logs
```

The most important collection is:

```text
parking_records
```

It stores the full lifecycle:

```text
Entry → Active → Exit → Fee Calculation → Cash Payment → Completed
```

Payments, OCR data, slot text, and pricing snapshots are embedded inside parking records to keep the MVP simple.