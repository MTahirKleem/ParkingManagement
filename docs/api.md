
# ParkingManagement API Contract

## 1. API Overview

This document defines the REST API contract for the ParkingManagement backend.

The backend is built with FastAPI and exposes APIs for:

* Authentication
* Current user profile
* Guard user management
* Vehicle entry
* Vehicle exit
* Vehicle search
* Parking history
* Pricing rules
* Dashboard
* Reports
* Settings
* Audit logs
* OCR later

The API should follow a clean layered backend architecture:

```text
API Router
    ↓
Service Layer
    ↓
Repository Layer
    ↓
MongoDB
```

Routers should stay thin. Business logic should stay inside services. Database queries should stay inside repositories.

## 2. Base URL

Development base URL:

```text
http://localhost:8000/api/v1
```

Frontend development URL:

```text
http://localhost:3000
```

## 3. Authentication Method

The API uses JWT authentication.

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

JWT payload:

```json
{
  "sub": "66a000000000000000000001",
  "role": "admin",
  "exp": 1760000000
}
```

## 4. Roles

ParkingManagement MVP has two roles:

```text
admin
guard
```

## 5. Role Permissions Summary

| Module                    | Admin | Guard |
| ------------------------- | ----: | ----: |
| Login                     |   Yes |   Yes |
| View own profile          |   Yes |   Yes |
| Create guards             |   Yes |    No |
| Update guards             |   Yes |    No |
| Delete guards             |   Yes |    No |
| Reset guard password      |   Yes |    No |
| Add vehicle entry         |   Yes |   Yes |
| Complete vehicle exit     |   Yes |   Yes |
| Search active vehicles    |   Yes |   Yes |
| Search completed vehicles |   Yes |   Yes |
| View parking history      |   Yes |   Yes |
| Edit parking record       |   Yes |    No |
| Delete parking record     |   Yes |    No |
| View admin dashboard      |   Yes |    No |
| View guard dashboard      |   Yes |   Yes |
| Manage pricing            |   Yes |    No |
| View reports              |   Yes |    No |
| Export PDF                |   Yes |    No |
| Export Excel              |   Yes |    No |
| Manage settings           |   Yes |    No |
| View audit logs           |   Yes |    No |

## 6. Standard Success Response

All API responses should follow a consistent shape.

```json
{
  "success": true,
  "message": "Request completed successfully",
  "data": {}
}
```

For list responses:

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

## 7. Standard Error Response

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

## 8. Common HTTP Status Codes

| Status Code | Meaning               |
| ----------: | --------------------- |
|         200 | Success               |
|         201 | Created               |
|         400 | Bad request           |
|         401 | Unauthorized          |
|         403 | Forbidden             |
|         404 | Not found             |
|         409 | Conflict              |
|         422 | Validation error      |
|         500 | Internal server error |

## 9. Common Error Codes

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

## 10. Auth APIs

## 10.1 Login

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

## 10.2 Get Current User

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

## 10.3 Refresh Token

Endpoint:

```http
POST /auth/refresh
```

Access:

```text
Admin, Guard
```

Note:

For MVP, refresh token can be skipped initially. The system can start with access token only and add refresh tokens later.

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

## 11. User APIs

User APIs are mainly for Admin to manage Guard accounts.

## 11.1 Create Guard

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

## 11.2 Get Users

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

## 11.3 Get User By ID

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

## 11.4 Update User

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
* Email should not be changed in MVP unless required later.
* Admin cannot accidentally delete the only Admin account.
* Create audit log with action `USER_UPDATED`.

## 11.5 Delete User

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

## 11.6 Reset User Password

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

## 12. Parking APIs

## 12.1 Create Vehicle Entry

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

## 12.2 Complete Vehicle Exit

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

## 12.3 Get Active Vehicles

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

## 12.4 Get Parking History

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

## 12.5 Search Parking Records

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
* User can search `LEA-1234`, `LEA 1234`, `lea1234`, or `LEA1234`.
* All should match the same normalized value.

## 12.6 Get Parking Record By ID

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
      "received_at": "2026-06-29T13:31:00Z"
    },
    "pricing_snapshot": {
      "pricing_rule_id": "66b000000000000000000002",
      "pricing_type": "hourly",
      "base_hours": 2,
      "base_fee": 100,
      "extra_hour_fee": 50,
      "grace_minutes": 10
    },
    "created_by": "66a000000000000000000002",
    "completed_by": "66a000000000000000000002",
    "created_at": "2026-06-29T10:00:00Z",
    "updated_at": "2026-06-29T13:31:00Z"
  }
}
```

## 12.7 Update Parking Record

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

## 12.8 Delete Parking Record

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

## 13. Pricing APIs

## 13.1 Get Pricing Rules

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
      "pricing_type": "hourly",
      "fixed_rate": null,
      "base_hours": 2,
      "base_fee": 100,
      "extra_hour_fee": 50,
      "grace_minutes": 10,
      "currency": "PKR",
      "is_active": true
    }
  ]
}
```

## 13.2 Update Pricing Rule

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

## 14. Dashboard APIs

## 14.1 Admin Dashboard

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

## 14.2 Guard Dashboard

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

## 15. Report APIs

## 15.1 Daily Report

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

## 15.2 Weekly Report

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

## 15.3 Monthly Report

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

## 15.4 Custom Date Range Report

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

## 15.5 Export PDF

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

Alternative query for range:

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

## 15.6 Export Excel

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

## 16. Settings APIs

## 16.1 Get Settings

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

## 16.2 Update Settings

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

## 17. Audit Log APIs

## 17.1 Get Audit Logs

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

## 18. OCR APIs Later

OCR is not required for the first implementation.

Manual plate entry must always work.

## 18.1 Detect Plate From Image

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

## 19. API Endpoint Summary

## Auth

```text
POST /auth/login
GET /auth/me
POST /auth/refresh
```

## Users

```text
POST /users
GET /users
GET /users/{user_id}
PUT /users/{user_id}
DELETE /users/{user_id}
POST /users/{user_id}/reset-password
```

## Parking

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

## Pricing

```text
GET /pricing
PUT /pricing/{pricing_id}
```

## Dashboard

```text
GET /dashboard/admin
GET /dashboard/guard
```

## Reports

```text
GET /reports/daily
GET /reports/weekly
GET /reports/monthly
GET /reports/custom
GET /reports/export/pdf
GET /reports/export/excel
```

## Settings

```text
GET /settings
PUT /settings
```

## Audit Logs

```text
GET /audit-logs
```

## OCR Later

```text
POST /ocr/plate
```

## 20. Implementation Order

Implement APIs in this order:

```text
1. Auth APIs
2. Current user API
3. User management APIs
4. Pricing APIs
5. Parking entry API
6. Parking exit API
7. Active vehicle API
8. Parking history and search APIs
9. Dashboard APIs
10. Report APIs
11. Export APIs
12. Settings APIs
13. Audit log APIs
14. OCR API later
```

## 21. Final Notes

The ParkingManagement API should be simple, predictable, and easy for the Next.js frontend to consume.

The most important API rules are:

* Use JWT authentication.
* Protect routes by role.
* Keep response format consistent.
* Normalize plate numbers for search.
* Prevent duplicate active vehicles.
* Calculate fee only during vehicle exit.
* Store cash payment inside parking record.
* Store pricing snapshot inside completed parking record.
* Count revenue only from completed records with cash received.
* Keep OCR optional.
* Keep routers thin and business logic inside services.


