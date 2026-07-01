
# Phase 4 – ParkingManagement REST API Design

## 1. Phase Goal

The goal of Phase 4 is to finalize the REST API contract before writing backend code.

This phase defines:

* API base URL
* Authentication method
* Role-based access rules
* Request body structure
* Response body structure
* Error response format
* Endpoint list
* Business rules per endpoint
* Implementation order

No FastAPI routes should be written before this contract is finalized.

## 2. API Base URL

Local development backend URL:

```text
http://localhost:8000
```

API version prefix:

```text
/api/v1
```

Full API base URL:

```text
http://localhost:8000/api/v1
```

## 3. API Design Rules

All APIs should follow these rules:

* Use REST-style endpoint naming.
* Use JSON request bodies.
* Use JSON responses.
* Use JWT authentication for protected routes.
* Use role-based authorization.
* Keep route handlers thin.
* Put business logic in services.
* Put database operations in repositories.
* Validate request input with Pydantic schemas.
* Return consistent response formats.
* Never return password hashes.
* Never expose JWT secrets.
* Use soft delete for important business records.

## 4. Authentication Method

Protected APIs require JWT authentication.

Header format:

```http
Authorization: Bearer <access_token>
```

JWT payload should contain:

```json
{
  "sub": "user_id",
  "role": "admin",
  "exp": 1760000000
}
```

Where:

```text
sub = logged-in user id
role = admin or guard
exp = token expiry timestamp
```

## 5. Roles

ParkingManagement MVP has two roles:

```text
admin
guard
```

## 6. Role Access Summary

| Module                | Admin | Guard |
| --------------------- | ----: | ----: |
| Login                 |   Yes |   Yes |
| Current user profile  |   Yes |   Yes |
| Create guard          |   Yes |    No |
| View guards           |   Yes |    No |
| Update guard          |   Yes |    No |
| Delete guard          |   Yes |    No |
| Reset guard password  |   Yes |    No |
| Create vehicle entry  |   Yes |   Yes |
| Complete vehicle exit |   Yes |   Yes |
| Search vehicles       |   Yes |   Yes |
| View active vehicles  |   Yes |   Yes |
| View parking history  |   Yes |   Yes |
| Edit parking record   |   Yes |    No |
| Delete parking record |   Yes |    No |
| View admin dashboard  |   Yes |    No |
| View guard dashboard  |   Yes |   Yes |
| View pricing          |   Yes |   Yes |
| Update pricing        |   Yes |    No |
| View reports          |   Yes |    No |
| Export PDF            |   Yes |    No |
| Export Excel          |   Yes |    No |
| View settings         |   Yes |   Yes |
| Update settings       |   Yes |    No |
| View audit logs       |   Yes |    No |
| OCR later             |   Yes |   Yes |

## 7. Standard Success Response

Single object response:

```json
{
  "success": true,
  "message": "Request completed successfully",
  "data": {}
}
```

List response:

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## 8. Standard Error Response

```json
{
  "success": false,
  "message": "Something went wrong",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

Example:

```json
{
  "success": false,
  "message": "Active vehicle with this plate number already exists",
  "error_code": "DUPLICATE_ACTIVE_VEHICLE",
  "details": {
    "plate_number": "LEA-1234"
  }
}
```

## 9. HTTP Status Codes

| Status Code | Meaning               |
| ----------: | --------------------- |
|         200 | Request successful    |
|         201 | Resource created      |
|         400 | Bad request           |
|         401 | Unauthorized          |
|         403 | Forbidden             |
|         404 | Resource not found    |
|         409 | Conflict              |
|         422 | Validation error      |
|         500 | Internal server error |

## 10. Common Error Codes

```text
INVALID_CREDENTIALS
TOKEN_EXPIRED
TOKEN_INVALID
UNAUTHORIZED
FORBIDDEN
VALIDATION_ERROR
USER_NOT_FOUND
USER_ALREADY_EXISTS
USER_INACTIVE
PARKING_RECORD_NOT_FOUND
DUPLICATE_ACTIVE_VEHICLE
VEHICLE_ALREADY_COMPLETED
PRICING_RULE_NOT_FOUND
INVALID_DATE_RANGE
SETTINGS_NOT_FOUND
INTERNAL_SERVER_ERROR
```

## 11. Endpoint Summary

## Auth APIs

```text
POST /auth/login
GET /auth/me
POST /auth/refresh
```

## User APIs

```text
POST /users
GET /users
GET /users/{user_id}
PUT /users/{user_id}
DELETE /users/{user_id}
POST /users/{user_id}/reset-password
```

## Parking APIs

```text
POST /parking/entry
POST /parking/{record_id}/exit
GET /parking/active
GET /parking/history
GET /parking/search
GET /parking/{record_id}
PUT /parking/{record_id}
DELETE /parking/{record_id}
```

## Pricing APIs

```text
GET /pricing
PUT /pricing/{pricing_id}
```

## Dashboard APIs

```text
GET /dashboard/admin
GET /dashboard/guard
```

## Report APIs

```text
GET /reports/daily
GET /reports/weekly
GET /reports/monthly
GET /reports/custom
GET /reports/export/pdf
GET /reports/export/excel
```

## Settings APIs

```text
GET /settings
PUT /settings
```

## Audit Log APIs

```text
GET /audit-logs
```

## OCR APIs Later

```text
POST /ocr/plate
```

# 12. Auth APIs

## 12.1 Login

Endpoint:

```http
POST /auth/login
```

Access:

```text
Public
```

Request:

```json
{
  "email": "admin@parkingmanagement.com",
  "password": "Admin@123"
}
```

Response:

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {
      "id": "66a000000000000000000001",
      "name": "System Admin",
      "email": "admin@parkingmanagement.com",
      "role": "admin",
      "status": "active"
    }
  }
}
```

Business rules:

* User email must exist.
* Password must match hashed password.
* User status must be `active`.
* On successful login, update `last_login_at`.
* Create audit log with action `USER_LOGIN`.
* On failed login, create audit log with action `USER_LOGIN_FAILED`.
* Never return password hash.

## 12.2 Get Current User

Endpoint:

```http
GET /auth/me
```

Access:

```text
Admin, Guard
```

Headers:

```http
Authorization: Bearer <access_token>
```

Response:

```json
{
  "success": true,
  "message": "Current user fetched successfully",
  "data": {
    "id": "66a000000000000000000001",
    "name": "System Admin",
    "email": "admin@parkingmanagement.com",
    "phone": "+923001111111",
    "role": "admin",
    "status": "active",
    "last_login_at": "2026-06-29T10:00:00Z"
  }
}
```

## 12.3 Refresh Token

Endpoint:

```http
POST /auth/refresh
```

Access:

```text
Admin, Guard
```

MVP note:

Refresh token can be skipped initially. The first implementation can use access token only.

Response:

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "new_jwt_token_here",
    "token_type": "bearer"
  }
}
```

# 13. User APIs

User APIs are mainly used by Admin to manage Guard accounts.

## 13.1 Create Guard

Endpoint:

```http
POST /users
```

Access:

```text
Admin only
```

Request:

```json
{
  "name": "Ali Guard",
  "email": "guard@parkingmanagement.com",
  "phone": "+923002222222",
  "password": "Guard@123",
  "role": "guard"
}
```

Response:

```json
{
  "success": true,
  "message": "Guard created successfully",
  "data": {
    "id": "66a000000000000000000002",
    "name": "Ali Guard",
    "email": "guard@parkingmanagement.com",
    "phone": "+923002222222",
    "role": "guard",
    "status": "active",
    "created_at": "2026-06-29T10:00:00Z"
  }
}
```

Business rules:

* Only Admin can create users.
* MVP allows Admin to create Guard accounts.
* Email must be unique.
* Password must be hashed before saving.
* Default status should be `active`.
* Create audit log with action `USER_CREATED`.

## 13.2 Get Users

Endpoint:

```http
GET /users
```

Access:

```text
Admin only
```

Query parameters:

```text
page=1
limit=20
role=guard
status=active
search=ali
```

Response:

```json
{
  "success": true,
  "message": "Users fetched successfully",
  "data": [
    {
      "id": "66a000000000000000000002",
      "name": "Ali Guard",
      "email": "guard@parkingmanagement.com",
      "phone": "+923002222222",
      "role": "guard",
      "status": "active",
      "created_at": "2026-06-29T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

## 13.3 Get User By ID

Endpoint:

```http
GET /users/{user_id}
```

Access:

```text
Admin only
```

Response:

```json
{
  "success": true,
  "message": "User fetched successfully",
  "data": {
    "id": "66a000000000000000000002",
    "name": "Ali Guard",
    "email": "guard@parkingmanagement.com",
    "phone": "+923002222222",
    "role": "guard",
    "status": "active",
    "last_login_at": null,
    "created_at": "2026-06-29T10:00:00Z",
    "updated_at": "2026-06-29T10:00:00Z"
  }
}
```

## 13.4 Update User

Endpoint:

```http
PUT /users/{user_id}
```

Access:

```text
Admin only
```

Request:

```json
{
  "name": "Ali Khan",
  "phone": "+923003333333",
  "status": "active"
}
```

Response:

```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "id": "66a000000000000000000002",
    "name": "Ali Khan",
    "email": "guard@parkingmanagement.com",
    "phone": "+923003333333",
    "role": "guard",
    "status": "active",
    "updated_at": "2026-06-29T11:00:00Z"
  }
}
```

Business rules:

* Only Admin can update users.
* Email should not be changed in MVP.
* Password cannot be updated from this endpoint.
* Create audit log with action `USER_UPDATED`.

## 13.5 Delete User

Endpoint:

```http
DELETE /users/{user_id}
```

Access:

```text
Admin only
```

Response:

```json
{
  "success": true,
  "message": "User deleted successfully",
  "data": {
    "id": "66a000000000000000000002",
    "status": "deleted"
  }
}
```

Business rules:

* Use soft delete.
* Set `status = deleted`.
* Deleted users cannot log in.
* Create audit log with action `USER_DELETED`.

## 13.6 Reset User Password

Endpoint:

```http
POST /users/{user_id}/reset-password
```

Access:

```text
Admin only
```

Request:

```json
{
  "new_password": "NewGuard@123"
}
```

Response:

```json
{
  "success": true,
  "message": "Password reset successfully",
  "data": {
    "id": "66a000000000000000000002"
  }
}
```

Business rules:

* Password must be hashed.
* Never return password or password hash.
* Create audit log with action `USER_PASSWORD_RESET`.

# 14. Parking APIs

## 14.1 Create Vehicle Entry

Endpoint:

```http
POST /parking/entry
```

Access:

```text
Admin, Guard
```

Request:

```json
{
  "plate_number": "LEA-1234",
  "vehicle_type": "bike",
  "slot": "A-12"
}
```

Response:

```json
{
  "success": true,
  "message": "Vehicle entry created successfully",
  "data": {
    "id": "66c000000000000000000001",
    "plate_number": "LEA-1234",
    "normalized_plate_number": "LEA1234",
    "vehicle_type": "bike",
    "slot": "A-12",
    "entry_time": "2026-06-29T10:00:00Z",
    "status": "active",
    "created_by": "66a000000000000000000002",
    "created_by_name": "Entry Guard",
    "created_at": "2026-06-29T10:00:00Z"
  }
}
```

Business rules:

* Plate number is required.
* Vehicle type is required.
* Vehicle type must be `bike` or `car`.
* Entry time is automatic.
* Status is `active`.
* Normalize plate number before saving.
* Same active normalized plate number cannot exist twice.
* Create audit log with action `VEHICLE_ENTRY_CREATED`.

## 14.2 Complete Vehicle Exit

Endpoint:

```http
POST /parking/{record_id}/exit
```

Access:

```text
Admin, Guard
```

Request:

```json
{
  "payment_received": true
}
```

Response:

```json
{
  "success": true,
  "message": "Vehicle exit completed successfully",
  "data": {
    "id": "66c000000000000000000001",
    "plate_number": "LEA-1234",
    "vehicle_type": "bike",
    "entry_time": "2026-06-29T10:00:00Z",
    "exit_time": "2026-06-29T12:15:00Z",
    "duration_minutes": 135,
    "fee": 50,
    "currency": "PKR",
    "status": "completed",
    "payment": {
      "method": "cash",
      "received": true,
      "received_by": "66a000000000000000000002",
      "received_by_name": "Exit Guard",
      "received_at": "2026-06-29T12:16:00Z"
    }
  }
}
```

Business rules:

* Record must exist.
* Record must have `status = active`.
* Completed vehicle cannot be exited again.
* Exit time is automatic.
* Fee is calculated by Pricing Service.
* Payment method is `cash`.
* Payment must be marked as received.
* Store pricing snapshot.
* Set status to `completed`.
* Create audit log with action `VEHICLE_EXIT_COMPLETED`.

## 14.3 Get Active Vehicles

Endpoint:

```http
GET /parking/active
```

Access:

```text
Admin, Guard
```

Query parameters:

```text
page=1
limit=20
search=LEA
vehicle_type=bike
```

Response:

```json
{
  "success": true,
  "message": "Active vehicles fetched successfully",
  "data": [
    {
      "id": "66c000000000000000000001",
      "plate_number": "LEA-1234",
      "vehicle_type": "bike",
      "slot": "A-12",
      "entry_time": "2026-06-29T10:00:00Z",
      "status": "active",
      "created_by": {
        "id": "66a000000000000000000002",
        "name": "Ali Guard"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

## 14.4 Get Parking History

Endpoint:

```http
GET /parking/history
```

Access:

```text
Admin, Guard
```

Query parameters:

```text
page=1
limit=20
status=completed
vehicle_type=car
start_date=2026-06-01
end_date=2026-06-29
search=LEA
```

Response:

```json
{
  "success": true,
  "message": "Parking history fetched successfully",
  "data": [
    {
      "id": "66c000000000000000000002",
      "plate_number": "LEA-5678",
      "vehicle_type": "car",
      "slot": "B-04",
      "entry_time": "2026-06-29T10:00:00Z",
      "exit_time": "2026-06-29T13:30:00Z",
      "duration_minutes": 210,
      "fee": 200,
      "currency": "PKR",
      "status": "completed",
      "payment": {
        "method": "cash",
        "received": true
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

## 14.5 Search Parking Records

Endpoint:

```http
GET /parking/search
```

Access:

```text
Admin, Guard
```

Query parameters:

```text
plate_number=LEA-1234
status=active
```

Response:

```json
{
  "success": true,
  "message": "Parking records found successfully",
  "data": [
    {
      "id": "66c000000000000000000001",
      "plate_number": "LEA-1234",
      "normalized_plate_number": "LEA1234",
      "vehicle_type": "bike",
      "slot": "A-12",
      "entry_time": "2026-06-29T10:00:00Z",
      "status": "active"
    }
  ]
}
```

Business rules:

* Search should use normalized plate number.
* Inputs like `LEA-1234`, `LEA 1234`, `lea1234`, and `LEA1234` should match the same record.
* Deleted records should not appear in normal search results.

## 14.6 Get Parking Record By ID

Endpoint:

```http
GET /parking/{record_id}
```

Access:

```text
Admin, Guard
```

Response:

```json
{
  "success": true,
  "message": "Parking record fetched successfully",
  "data": {
    "id": "66c000000000000000000002",
    "plate_number": "LEA-5678",
    "normalized_plate_number": "LEA5678",
    "vehicle_type": "car",
    "slot": "B-04",
    "entry_time": "2026-06-29T10:00:00Z",
    "exit_time": "2026-06-29T13:30:00Z",
    "duration_minutes": 210,
    "fee": 200,
    "currency": "PKR",
    "status": "completed",
    "payment": {
      "method": "cash",
      "received": true,
      "received_by": "66a000000000000000000002",
      "received_by_name": "Exit Guard",
      "received_at": "2026-06-29T13:31:00Z"
    },
    "created_by": "66a000000000000000000002",
    "created_by_name": "Entry Guard",
    "completed_by": "66a000000000000000000002",
    "completed_by_name": "Exit Guard",
    "created_at": "2026-06-29T10:00:00Z",
    "updated_at": "2026-06-29T13:31:00Z"
  }
}
```

## 14.7 Update Parking Record

Endpoint:

```http
PUT /parking/{record_id}
```

Access:

```text
Admin only
```

Request:

```json
{
  "plate_number": "LEA-9999",
  "vehicle_type": "car",
  "slot": "B-05",
  "notes": "Plate number corrected by admin"
}
```

Response:

```json
{
  "success": true,
  "message": "Parking record updated successfully",
  "data": {
    "id": "66c000000000000000000002",
    "plate_number": "LEA-9999",
    "normalized_plate_number": "LEA9999",
    "vehicle_type": "car",
    "slot": "B-05",
    "notes": "Plate number corrected by admin",
    "updated_at": "2026-06-29T14:00:00Z"
  }
}
```

Business rules:

* Only Admin can update parking records.
* If plate number changes, normalized plate number must also update.
* Admin updates must create audit log with action `PARKING_RECORD_UPDATED`.

## 14.8 Delete Parking Record

Endpoint:

```http
DELETE /parking/{record_id}
```

Access:

```text
Admin only
```

Response:

```json
{
  "success": true,
  "message": "Parking record deleted successfully",
  "data": {
    "id": "66c000000000000000000002",
    "status": "deleted"
  }
}
```

Business rules:

* Use soft delete.
* Set `status = deleted`.
* Deleted records should not appear in revenue reports.
* Create audit log with action `PARKING_RECORD_DELETED`.

# 15. Pricing APIs

## 15.1 Get Pricing Rules

Endpoint:

```http
GET /pricing
```

Access:

```text
Admin, Guard
```

Response:

```json
{
  "success": true,
  "message": "Pricing rules fetched successfully",
  "data": [
    {
      "id": "66b000000000000000000001",
      "vehicle_type": "bike",
      "pricing_type": "fixed",
      "fixed_rate": 50,
      "base_hours": null,
      "base_fee": null,
      "extra_hour_fee": null,
      "grace_minutes": 0,
      "currency": "PKR",
      "is_active": true
    },
    {
      "id": "66b000000000000000000002",
      "vehicle_type": "car",
      "pricing_type": "fixed",
      "fixed_rate": 100,
      "base_hours": null,
      "base_fee": null,
      "extra_hour_fee": null,
      "grace_minutes": 0,
      "currency": "PKR",
      "is_active": true
    }
  ]
}
```

## 15.2 Update Pricing Rule

Endpoint:

```http
PUT /pricing/{pricing_id}
```

Access:

```text
Admin only
```

Request for fixed pricing:

```json
{
  "vehicle_type": "bike",
  "pricing_type": "fixed",
  "fixed_rate": 50,
  "grace_minutes": 0,
  "currency": "PKR",
  "is_active": true
}
```

Request for hourly pricing:

```json
{
  "vehicle_type": "car",
  "pricing_type": "hourly",
  "fixed_rate": null,
  "base_hours": 2,
  "base_fee": 100,
  "extra_hour_fee": 50,
  "grace_minutes": 10,
  "currency": "PKR",
  "is_active": true
}
```

Response:

```json
{
  "success": true,
  "message": "Pricing rule updated successfully",
  "data": {
    "id": "66b000000000000000000002",
    "vehicle_type": "car",
    "pricing_type": "hourly",
    "base_hours": 2,
    "base_fee": 100,
    "extra_hour_fee": 50,
    "grace_minutes": 10,
    "currency": "PKR",
    "is_active": true,
    "updated_at": "2026-06-29T14:00:00Z"
  }
}
```

Business rules:

* Only Admin can update pricing.
* Vehicle type must be `bike` or `car`.
* Pricing type must be `fixed` or `hourly`.
* If pricing type is `fixed`, `fixed_rate` is required.
* If pricing type is `hourly`, `base_hours`, `base_fee`, and `extra_hour_fee` are required.
* Pricing changes affect future exits only.
* Existing completed records should keep their old fee.
* Create audit log with action `PRICING_RULE_UPDATED`.

# 16. Dashboard APIs

## 16.1 Admin Dashboard

Endpoint:

```http
GET /dashboard/admin
```

Access:

```text
Admin only
```

Response:

```json
{
  "success": true,
  "message": "Admin dashboard fetched successfully",
  "data": {
    "total_revenue": 250000,
    "today_revenue": 12500,
    "monthly_revenue": 80000,
    "active_vehicles": 42,
    "today_entries": 120,
    "today_exits": 78,
    "completed_vehicles": 78,
    "parking_capacity": 100,
    "occupancy_percentage": 42,
    "revenue_by_vehicle_type": [
      {
        "vehicle_type": "bike",
        "revenue": 5000
      },
      {
        "vehicle_type": "car",
        "revenue": 7500
      }
    ],
    "revenue_by_guard": [
      {
        "guard_id": "66a000000000000000000002",
        "guard_name": "Ali Guard",
        "revenue": 12500
      }
    ],
    "recent_transactions": [
      {
        "id": "66c000000000000000000002",
        "plate_number": "LEA-5678",
        "vehicle_type": "car",
        "fee": 200,
        "exit_time": "2026-06-29T13:30:00Z"
      }
    ]
  }
}
```

Business rules:

* Revenue counts only completed records with `payment.received = true`.
* Active vehicles are records with `status = active`.
* Occupancy uses `settings.parking_capacity`.
* Recent transactions use completed records sorted by exit time.

## 16.2 Guard Dashboard

Endpoint:

```http
GET /dashboard/guard
```

Access:

```text
Admin, Guard
```

Response:

```json
{
  "success": true,
  "message": "Guard dashboard fetched successfully",
  "data": {
    "active_vehicles": 42,
    "today_entries": 18,
    "today_exits": 12,
    "recent_entries": [
      {
        "id": "66c000000000000000000001",
        "plate_number": "LEA-1234",
        "vehicle_type": "bike",
        "entry_time": "2026-06-29T10:00:00Z",
        "status": "active"
      }
    ]
  }
}
```

Business rules:

* Guard dashboard should be simple.
* Guard should not see full revenue analytics in MVP.
* Guard can see operational counts and recent entries.

# 17. Report APIs

## 17.1 Daily Report

Endpoint:

```http
GET /reports/daily
```

Access:

```text
Admin only
```

Query parameters:

```text
date=2026-06-29
```

Response:

```json
{
  "success": true,
  "message": "Daily report generated successfully",
  "data": {
    "date": "2026-06-29",
    "total_revenue": 12500,
    "total_completed": 78,
    "total_entries": 120,
    "bike_count": 45,
    "car_count": 33,
    "bike_revenue": 5000,
    "car_revenue": 7500,
    "revenue_by_guard": [
      {
        "guard_id": "66a000000000000000000002",
        "guard_name": "Ali Guard",
        "revenue": 12500,
        "completed_count": 78
      }
    ]
  }
}
```

## 17.2 Weekly Report

Endpoint:

```http
GET /reports/weekly
```

Access:

```text
Admin only
```

Query parameters:

```text
start_date=2026-06-23
end_date=2026-06-29
```

Response:

```json
{
  "success": true,
  "message": "Weekly report generated successfully",
  "data": {
    "start_date": "2026-06-23",
    "end_date": "2026-06-29",
    "total_revenue": 70000,
    "total_completed": 420,
    "total_entries": 510,
    "daily_breakdown": [
      {
        "date": "2026-06-29",
        "revenue": 12500,
        "completed_count": 78
      }
    ]
  }
}
```

## 17.3 Monthly Report

Endpoint:

```http
GET /reports/monthly
```

Access:

```text
Admin only
```

Query parameters:

```text
year=2026
month=6
```

Response:

```json
{
  "success": true,
  "message": "Monthly report generated successfully",
  "data": {
    "year": 2026,
    "month": 6,
    "total_revenue": 250000,
    "total_completed": 1600,
    "total_entries": 1800,
    "bike_revenue": 90000,
    "car_revenue": 160000,
    "daily_breakdown": [
      {
        "date": "2026-06-29",
        "revenue": 12500,
        "completed_count": 78
      }
    ]
  }
}
```

## 17.4 Custom Date Range Report

Endpoint:

```http
GET /reports/custom
```

Access:

```text
Admin only
```

Query parameters:

```text
start_date=2026-06-01
end_date=2026-06-29
```

Response:

```json
{
  "success": true,
  "message": "Custom report generated successfully",
  "data": {
    "start_date": "2026-06-01",
    "end_date": "2026-06-29",
    "total_revenue": 250000,
    "total_completed": 1600,
    "total_entries": 1800,
    "vehicle_type_breakdown": [
      {
        "vehicle_type": "bike",
        "count": 900,
        "revenue": 90000
      },
      {
        "vehicle_type": "car",
        "count": 700,
        "revenue": 160000
      }
    ],
    "guard_breakdown": [
      {
        "guard_id": "66a000000000000000000002",
        "guard_name": "Ali Guard",
        "completed_count": 600,
        "revenue": 90000
      }
    ]
  }
}
```

## 17.5 Export PDF

Endpoint:

```http
GET /reports/export/pdf
```

Access:

```text
Admin only
```

Query parameters:

```text
report_type=daily
date=2026-06-29
```

Alternative:

```text
report_type=custom
start_date=2026-06-01
end_date=2026-06-29
```

Response:

```text
PDF file download
```

Business rules:

* Only Admin can export PDF.
* Export should use report data from Report Service.
* Create audit log with action `EXPORT_PDF_GENERATED`.

## 17.6 Export Excel

Endpoint:

```http
GET /reports/export/excel
```

Access:

```text
Admin only
```

Query parameters:

```text
report_type=monthly
year=2026
month=6
```

Response:

```text
Excel file download
```

Business rules:

* Only Admin can export Excel.
* Export should use report data from Report Service.
* Create audit log with action `EXPORT_EXCEL_GENERATED`.

# 18. Settings APIs

## 18.1 Get Settings

Endpoint:

```http
GET /settings
```

Access:

```text
Admin, Guard
```

Response:

```json
{
  "success": true,
  "message": "Settings fetched successfully",
  "data": {
    "id": "66d000000000000000000001",
    "parking_name": "ParkingManagement",
    "address": "Lahore, Pakistan",
    "phone": "+923001234567",
    "currency": "PKR",
    "logo_url": null,
    "receipt_footer": "Thank you for parking with us.",
    "parking_capacity": 100,
    "timezone": "Asia/Karachi"
  }
}
```

## 18.2 Update Settings

Endpoint:

```http
PUT /settings
```

Access:

```text
Admin only
```

Request:

```json
{
  "parking_name": "ParkingManagement",
  "address": "Main Boulevard, Lahore",
  "phone": "+923001234567",
  "currency": "PKR",
  "logo_url": null,
  "receipt_footer": "Thank you for parking with us.",
  "parking_capacity": 100,
  "timezone": "Asia/Karachi"
}
```

Response:

```json
{
  "success": true,
  "message": "Settings updated successfully",
  "data": {
    "id": "66d000000000000000000001",
    "parking_name": "ParkingManagement",
    "address": "Main Boulevard, Lahore",
    "phone": "+923001234567",
    "currency": "PKR",
    "logo_url": null,
    "receipt_footer": "Thank you for parking with us.",
    "parking_capacity": 100,
    "timezone": "Asia/Karachi",
    "updated_at": "2026-06-29T14:00:00Z"
  }
}
```

Business rules:

* Only Admin can update settings.
* Parking capacity should be a positive number.
* Currency defaults to `PKR`.
* Timezone defaults to `Asia/Karachi`.
* Create audit log with action `SETTINGS_UPDATED`.

# 19. Audit Log APIs

## 19.1 Get Audit Logs

Endpoint:

```http
GET /audit-logs
```

Access:

```text
Admin only
```

Query parameters:

```text
page=1
limit=20
action=VEHICLE_ENTRY_CREATED
user_id=66a000000000000000000002
start_date=2026-06-01
end_date=2026-06-29
```

Response:

```json
{
  "success": true,
  "message": "Audit logs fetched successfully",
  "data": [
    {
      "id": "66e000000000000000000001",
      "user_id": "66a000000000000000000002",
      "user_role": "guard",
      "action": "VEHICLE_ENTRY_CREATED",
      "entity": "parking_record",
      "entity_id": "66c000000000000000000001",
      "message": "Vehicle entry created for LEA-1234",
      "metadata": {
        "plate_number": "LEA-1234",
        "vehicle_type": "bike"
      },
      "ip_address": "127.0.0.1",
      "created_at": "2026-06-29T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

Business rules:

* Only Admin can view audit logs.
* Audit logs are append-only.
* Audit logs should not be edited or deleted from the UI.
* Sensitive data should not be stored in metadata.

# 20. OCR APIs Later

OCR is not required for the first implementation.

Manual plate entry must always work.

## 20.1 Detect Plate From Image

Endpoint:

```http
POST /ocr/plate
```

Access:

```text
Admin, Guard
```

Request:

```http
multipart/form-data
file=<vehicle_image>
```

Response:

```json
{
  "success": true,
  "message": "Plate detected successfully",
  "data": {
    "plate": "LEA-1234",
    "confidence": 0.95,
    "image_url": "uploads/plates/temp_001.jpg"
  }
}
```

Business rules:

* OCR is optional.
* Guard must confirm or correct the plate before saving entry.
* OCR should not automatically create parking entry.
* OCR data should be stored inside parking record only if used.
* Manual entry must remain available.

# 21. API Implementation Order

Implement APIs in this order:

```text
1. Health check API
2. Auth login API
3. Current user API
4. User management APIs
5. Pricing APIs
6. Parking entry API
7. Parking exit API
8. Active vehicle API
9. Parking history API
10. Parking search API
11. Dashboard APIs
12. Report APIs
13. Export APIs
14. Settings APIs
15. Audit log APIs
16. OCR API later
```

# 22. Phase 4 Completion Checklist

Phase 4 is complete when:

```text
Base URL is finalized
Auth method is finalized
Role access is finalized
Response format is finalized
Error format is finalized
Auth endpoints are finalized
User endpoints are finalized
Parking endpoints are finalized
Pricing endpoints are finalized
Dashboard endpoints are finalized
Report endpoints are finalized
Settings endpoints are finalized
Audit log endpoints are finalized
OCR future endpoint is documented
Implementation order is finalized
```

# 23. Final API Summary

ParkingManagement API should be simple, predictable, and easy for the frontend to consume.

Core rules:

* Use `/api/v1` prefix.
* Use JWT authentication.
* Protect routes by role.
* Normalize plate numbers.
* Prevent duplicate active vehicles.
* Calculate fee only during vehicle exit.
* Store cash payment inside parking record.
* Store pricing snapshot inside completed parking record.
* Count revenue only from completed records with cash received.
* Keep OCR optional.
* Keep routers thin and business logic inside services.

