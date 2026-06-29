# ParkingManagement Database Design

## 1. Database Overview

ParkingManagement uses MongoDB as the primary database.

Database name:

```text
parkingmanagement
```

The MVP database is intentionally simple. The first version will use only five collections:

```text
users
parking_records
pricing_rules
settings
audit_logs
```

The following collections are not included in Version 1:

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

Payment information will be stored directly inside each parking record.

Parking slot information will be stored as an optional text field inside each parking record.

OCR data will also be stored inside the parking record when OCR is used.

## 2. Collection List

| Collection      | Purpose                                                |
| --------------- | ------------------------------------------------------ |
| users           | Stores Admin and Guard accounts                        |
| parking_records | Stores vehicle entry, exit, fee, payment, and OCR data |
| pricing_rules   | Stores bike and car pricing configuration              |
| settings        | Stores parking business settings                       |
| audit_logs      | Stores important system actions                        |

## 3. Global Database Rules

All collections should follow these common rules:

* Use MongoDB ObjectId as `_id`.
* Store all timestamps in UTC.
* Use ISO datetime format in API responses.
* Use lowercase enum values in backend code where possible.
* Never store plain-text passwords.
* Use soft delete where historical data matters.
* Store `created_at` and `updated_at` in main collections.
* Store `created_by` and `updated_by` where user tracking is required.
* Store important actions in `audit_logs`.

## 4. Enum Values

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

## 5. users Collection

The `users` collection stores Admin and Guard accounts.

Admins manage the system.

Guards handle vehicle entry, exit, search, and cash collection.

### Document Shape

```json
{
  "_id": "ObjectId",
  "name": "Ali Guard",
  "email": "guard@example.com",
  "phone": "+923001234567",
  "password_hash": "hashed_password",
  "role": "guard",
  "status": "active",
  "last_login_at": "2026-06-29T10:00:00Z",
  "created_by": "ObjectId",
  "updated_by": "ObjectId",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Field Details

| Field             | Type          | Required | Description                              |
| ----------------- | ------------- | -------- | ---------------------------------------- |
| `_id`           | ObjectId      | Yes      | MongoDB document ID                      |
| `name`          | string        | Yes      | User full name                           |
| `email`         | string        | Yes      | Unique login email                       |
| `phone`         | string/null   | No       | Optional phone number                    |
| `password_hash` | string        | Yes      | Hashed password                          |
| `role`          | string        | Yes      | `admin` or `guard`                   |
| `status`        | string        | Yes      | `active`, `inactive`, or `deleted` |
| `last_login_at` | datetime/null | No       | Last successful login time               |
| `created_by`    | ObjectId/null | No       | Admin who created the user               |
| `updated_by`    | ObjectId/null | No       | Last admin who updated the user          |
| `created_at`    | datetime      | Yes      | Created timestamp                        |
| `updated_at`    | datetime      | Yes      | Updated timestamp                        |

### Example Admin User

```json
{
  "_id": "66a000000000000000000001",
  "name": "System Admin",
  "email": "admin@parkingmanagement.com",
  "phone": "+923001111111",
  "password_hash": "$2b$12$hashed_password_here",
  "role": "admin",
  "status": "active",
  "last_login_at": null,
  "created_by": null,
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Example Guard User

```json
{
  "_id": "66a000000000000000000002",
  "name": "Ali Guard",
  "email": "guard@parkingmanagement.com",
  "phone": "+923002222222",
  "password_hash": "$2b$12$hashed_password_here",
  "role": "guard",
  "status": "active",
  "last_login_at": null,
  "created_by": "66a000000000000000000001",
  "updated_by": "66a000000000000000000001",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Indexes

```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ role: 1 })
db.users.createIndex({ status: 1 })
db.users.createIndex({ created_at: -1 })
```

### Business Rules

* Email must be unique.
* Password must never be stored as plain text.
* Only Admin can create, update, delete, or reset Guard accounts.
* Guard cannot create users.
* Deleted users should be soft deleted by setting `status` to `deleted`.
* Inactive or deleted users cannot log in.

## 6. parking_records Collection

The `parking_records` collection is the main collection of the system.

It stores:

* Vehicle entry
* Vehicle exit
* Parking duration
* Fee
* Cash payment status
* Guard who created entry
* Guard who completed exit
* Optional OCR result
* Optional slot text

### Document Shape

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
    "received_by": "66a000000000000000000002",
    "received_at": "2026-06-29T12:16:00Z"
  },
  "pricing_snapshot": {
    "pricing_rule_id": "66b000000000000000000001",
    "pricing_type": "fixed",
    "fixed_rate": 50,
    "base_hours": null,
    "base_fee": null,
    "extra_hour_fee": null,
    "grace_minutes": 0
  },
  "ocr": {
    "used": true,
    "plate": "LEA-1234",
    "confidence": 0.95,
    "image_url": "uploads/plates/record_001.jpg"
  },
  "notes": null,
  "created_by": "66a000000000000000000002",
  "completed_by": "66a000000000000000000002",
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T12:16:00Z"
}
```

### Field Details

| Field                       | Type          | Required | Description                                              |
| --------------------------- | ------------- | -------- | -------------------------------------------------------- |
| `_id`                     | ObjectId      | Yes      | MongoDB document ID                                      |
| `plate_number`            | string        | Yes      | Display plate number                                     |
| `normalized_plate_number` | string        | Yes      | Search-friendly plate number                             |
| `vehicle_type`            | string        | Yes      | `bike` or `car`                                      |
| `slot`                    | string/null   | No       | Optional slot text                                       |
| `entry_time`              | datetime      | Yes      | Automatic entry time                                     |
| `exit_time`               | datetime/null | No       | Automatic exit time                                      |
| `status`                  | string        | Yes      | `active`, `completed`, `cancelled`, or `deleted` |
| `duration_minutes`        | integer/null  | No       | Total parking duration after exit                        |
| `fee`                     | integer/null  | No       | Calculated fee after exit                                |
| `currency`                | string        | Yes      | Example:`PKR`                                          |
| `payment`                 | object/null   | No       | Cash payment object                                      |
| `pricing_snapshot`        | object/null   | No       | Pricing rule used at exit time                           |
| `ocr`                     | object/null   | No       | OCR result if used                                       |
| `notes`                   | string/null   | No       | Admin notes                                              |
| `created_by`              | ObjectId      | Yes      | Guard who created entry                                  |
| `completed_by`            | ObjectId/null | No       | Guard who completed exit                                 |
| `updated_by`              | ObjectId/null | No       | Admin who updated record                                 |
| `created_at`              | datetime      | Yes      | Created timestamp                                        |
| `updated_at`              | datetime      | Yes      | Updated timestamp                                        |

### Active Vehicle Example

```json
{
  "_id": "66c000000000000000000001",
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
  "created_by": "66a000000000000000000002",
  "completed_by": null,
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Completed Vehicle Example

```json
{
  "_id": "66c000000000000000000002",
  "plate_number": "LEA-5678",
  "normalized_plate_number": "LEA5678",
  "vehicle_type": "car",
  "slot": "B-04",
  "entry_time": "2026-06-29T10:00:00Z",
  "exit_time": "2026-06-29T13:30:00Z",
  "status": "completed",
  "duration_minutes": 210,
  "fee": 200,
  "currency": "PKR",
  "payment": {
    "method": "cash",
    "received": true,
    "received_by": "66a000000000000000000002",
    "received_at": "2026-06-29T13:31:00Z"
  },
  "pricing_snapshot": {
    "pricing_rule_id": "66b000000000000000000002",
    "pricing_type": "hourly",
    "fixed_rate": null,
    "base_hours": 2,
    "base_fee": 100,
    "extra_hour_fee": 50,
    "grace_minutes": 10
  },
  "ocr": {
    "used": false,
    "plate": null,
    "confidence": null,
    "image_url": null
  },
  "notes": null,
  "created_by": "66a000000000000000000002",
  "completed_by": "66a000000000000000000002",
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T13:31:00Z"
}
```

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

### Recommended Partial Unique Index

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

### Business Rules

* Plate number is required.
* Vehicle type is required.
* Entry time is automatic.
* Exit time is automatic.
* A vehicle starts with `status = active`.
* A completed vehicle has `status = completed`.
* Same active plate number cannot exist twice.
* Fee is calculated only during exit.
* Payment method is cash only in MVP.
* Revenue reports count only completed records with `payment.received = true`.
* Completed records cannot be exited again.
* Deleted records should not be counted in reports.
* Admin edits should update `updated_by` and create an audit log.
* Pricing changes should not change old completed records.
* Store `pricing_snapshot` inside parking record at exit time.

## 7. pricing_rules Collection

The `pricing_rules` collection stores bike and car pricing.

MVP supports:

```text
fixed
hourly
```

### Document Shape

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
  "created_by": "66a000000000000000000001",
  "updated_by": "66a000000000000000000001",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Field Details

| Field              | Type          | Required    | Description                    |
| ------------------ | ------------- | ----------- | ------------------------------ |
| `_id`            | ObjectId      | Yes         | MongoDB document ID            |
| `vehicle_type`   | string        | Yes         | `bike` or `car`            |
| `pricing_type`   | string        | Yes         | `fixed` or `hourly`        |
| `fixed_rate`     | integer/null  | Conditional | Required for fixed pricing     |
| `base_hours`     | integer/null  | Conditional | Required for hourly pricing    |
| `base_fee`       | integer/null  | Conditional | Required for hourly pricing    |
| `extra_hour_fee` | integer/null  | Conditional | Required for hourly pricing    |
| `grace_minutes`  | integer       | Yes         | Grace time before extra charge |
| `currency`       | string        | Yes         | Example:`PKR`                |
| `is_active`      | boolean       | Yes         | Active pricing rule            |
| `created_by`     | ObjectId/null | No          | Admin who created rule         |
| `updated_by`     | ObjectId/null | No          | Admin who updated rule         |
| `created_at`     | datetime      | Yes         | Created timestamp              |
| `updated_at`     | datetime      | Yes         | Updated timestamp              |

### Fixed Pricing Example

```json
{
  "_id": "66b000000000000000000001",
  "vehicle_type": "bike",
  "pricing_type": "fixed",
  "fixed_rate": 50,
  "base_hours": null,
  "base_fee": null,
  "extra_hour_fee": null,
  "grace_minutes": 0,
  "currency": "PKR",
  "is_active": true,
  "created_by": "66a000000000000000000001",
  "updated_by": "66a000000000000000000001",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Hourly Pricing Example

```json
{
  "_id": "66b000000000000000000002",
  "vehicle_type": "car",
  "pricing_type": "hourly",
  "fixed_rate": null,
  "base_hours": 2,
  "base_fee": 100,
  "extra_hour_fee": 50,
  "grace_minutes": 10,
  "currency": "PKR",
  "is_active": true,
  "created_by": "66a000000000000000000001",
  "updated_by": "66a000000000000000000001",
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:00:00Z"
}
```

### Indexes

```javascript
db.pricing_rules.createIndex({ vehicle_type: 1 })
db.pricing_rules.createIndex({ is_active: 1 })
db.pricing_rules.createIndex({ vehicle_type: 1,
```
