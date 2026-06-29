
# ParkingManagement

ParkingManagement is a modern parking management system for small and medium parking operations such as shopping malls, hospitals, residential societies, schools, office buildings, and private parking lots.

The goal of this project is to build a clean, scalable, and production-ready MVP that handles the complete parking workflow:

```text
Vehicle Entry → Active Parking → Vehicle Exit → Fee Calculation → Cash Payment → Completed Record
```

The first version focuses on the core parking system. Advanced features such as OCR, online payments, camera integration, boom barriers, RFID, mobile app, and SaaS multi-tenancy can be added later.

## Project Status

Current phase:

```text
Phase 2: Documentation and planning
```

Completed planning documents:

```text
docs/architecture.md
docs/database.md
docs/api.md
docs/workflow.md
```

Upcoming document:

```text
docs/deployment.md
```

## MVP Scope

### Included in Version 1

* Authentication
* JWT login
* Admin and Guard roles
* Vehicle entry
* Vehicle exit
* Vehicle search
* Parking history
* Automatic fee calculation
* Cash payment tracking
* Pricing rules
* Admin dashboard
* Guard dashboard
* Daily reports
* Weekly reports
* Monthly reports
* Custom date range reports
* PDF export
* Excel export
* Settings
* Audit logs

### Not Included in Version 1

* Online payments
* JazzCash
* EasyPaisa
* Stripe
* Camera integration
* Printer integration
* Boom barrier integration
* RFID
* Dedicated parking slots collection
* Multiple branches
* Multi-tenant billing
* Mobile app
* Advanced AI automation

OCR will be added later as an optional helper. Manual plate entry must always remain available.

## User Roles

ParkingManagement MVP has two roles:

```text
admin
guard
```

## Guard Role

The Guard is responsible for daily parking operations.

Guard can:

* Login
* Add vehicle entry
* Enter plate number manually
* Select vehicle type
* Add optional parking slot text
* Search active vehicles
* Search completed vehicles
* View parking details
* Mark vehicle exit
* Receive cash
* Complete parking session
* View simple dashboard

Guard dashboard includes:

* Active vehicles
* Today's entries
* Today's exits
* Recent entries

## Admin Role

The Admin manages the complete system.

Admin can:

* Create guard accounts
* Update guard accounts
* Delete guard accounts
* Reset guard passwords
* View all parking records
* Edit parking records
* Delete parking records
* Configure pricing
* Manage settings
* View dashboard
* View revenue
* Generate reports
* Export PDF
* Export Excel
* View audit logs

Admin dashboard includes:

* Total revenue
* Today's revenue
* Monthly revenue
* Active vehicles
* Completed vehicles
* Today's entries
* Today's exits
* Parking occupancy
* Revenue by guard
* Revenue by vehicle type
* Recent transactions

## Technology Stack

### Frontend

```text
Next.js App Router
TypeScript
Tailwind CSS
shadcn/ui
React Query
Axios
React Hook Form
Zod
```

### Backend

```text
Python 3.13+
FastAPI
Motor MongoDB Async Driver
Pydantic v2
JWT Authentication
Passlib
Async architecture
Repository + Service Pattern
```

### Database

```text
MongoDB
```

Development database name:

```text
parkingmanagement
```

## High-Level Architecture

```text
Next.js Frontend
        ↓
FastAPI Backend
        ↓
Service Layer
        ↓
Repository Layer
        ↓
MongoDB
```

Backend layers:

```text
API Router
    ↓
Service Layer
    ↓
Repository Layer
    ↓
MongoDB
```

## Repository Structure

```text
ParkingManagement/

├── backend/
├── frontend/
├── docs/
├── docker/
├── scripts/
├── .gitignore
├── README.md
└── docker-compose.yml
```

## Backend Structure

```text
backend/

app/
├── api/
│   └── v1/
│       ├── auth.py
│       ├── users.py
│       ├── parking.py
│       ├── pricing.py
│       ├── dashboard.py
│       ├── reports.py
│       ├── settings.py
│       └── ocr.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── permissions.py
│   └── constants.py
│
├── database/
│   └── mongodb.py
│
├── models/
│   ├── user.py
│   ├── parking_record.py
│   ├── pricing_rule.py
│   ├── settings.py
│   └── audit_log.py
│
├── schemas/
├── repositories/
├── services/
├── middleware/
├── utils/
└── main.py
```

## Frontend Structure

```text
frontend/

app/
├── login/
├── dashboard/
├── parking/
│   ├── entry/
│   ├── exit/
│   ├── active/
│   └── history/
├── users/
├── pricing/
├── reports/
├── settings/
└── layout.tsx

components/
hooks/
lib/
services/
types/
```

## Database Collections

The MVP uses only five collections:

```text
users
parking_records
pricing_rules
settings
audit_logs
```

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

Payment information is stored directly inside each parking record.

Parking slot information is stored as an optional text field inside each parking record.

OCR data will also be stored inside the parking record when OCR is used.

## Main Parking Record Shape

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
  "ocr": null,
  "notes": null,
  "created_by": "66a000000000000000000002",
  "completed_by": "66a000000000000000000002",
  "updated_by": null,
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T12:16:00Z"
}
```

## API Base URL

Development backend URL:

```text
http://localhost:8000/api/v1
```

Development frontend URL:

```text
http://localhost:3000
```

## Main API Modules

### Auth

```text
POST /auth/login
GET /auth/me
POST /auth/refresh
```

### Users

```text
POST /users
GET /users
GET /users/{user_id}
PUT /users/{user_id}
DELETE /users/{user_id}
POST /users/{user_id}/reset-password
```

### Parking

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

### Pricing

```text
GET /pricing
PUT /pricing/{pricing_id}
```

### Dashboard

```text
GET /dashboard/admin
GET /dashboard/guard
```

### Reports

```text
GET /reports/daily
GET /reports/weekly
GET /reports/monthly
GET /reports/custom
GET /reports/export/pdf
GET /reports/export/excel
```

### Settings

```text
GET /settings
PUT /settings
```

### Audit Logs

```text
GET /audit-logs
```

### OCR Later

```text
POST /ocr/plate
```

## Vehicle Entry Flow

```text
Guard opens Vehicle Entry screen
       ↓
Guard enters plate number
       ↓
Guard selects vehicle type: bike or car
       ↓
Guard optionally enters slot
       ↓
Guard clicks Save Entry
       ↓
Backend validates input
       ↓
Backend normalizes plate number
       ↓
Backend checks duplicate active vehicle
       ↓
Backend creates parking record
       ↓
Backend creates audit log
       ↓
Frontend shows success message
```

## Vehicle Exit Flow

```text
Guard searches active vehicle
       ↓
Guard opens vehicle details
       ↓
Guard clicks Mark Exit
       ↓
Backend verifies record exists
       ↓
Backend verifies status is active
       ↓
Backend records exit time
       ↓
Backend calculates duration
       ↓
Backend gets pricing rule
       ↓
Backend calculates fee
       ↓
Backend stores pricing snapshot
       ↓
Guard receives cash
       ↓
Backend stores payment object
       ↓
Backend marks status as completed
       ↓
Backend creates audit log
       ↓
Frontend shows completed parking session
```

## Business Rules

### Vehicle Entry Rules

* Plate number is required.
* Vehicle type is required.
* Vehicle type must be `bike` or `car`.
* Entry time is automatic.
* Parking status must be `active`.
* Same active plate number cannot exist twice.
* Plate number must be normalized before saving.
* Guard ID must be stored in `created_by`.

### Vehicle Exit Rules

* Record must exist.
* Record must be active.
* Completed record cannot be exited again.
* Exit time is automatic.
* Fee is calculated by the system.
* Payment method is cash only.
* Cash must be marked as received.
* Pricing snapshot must be stored.
* Status becomes `completed`.

### Report Rules

* Reports count only completed records.
* Revenue counts only records with `payment.received = true`.
* Active vehicles are not counted in revenue.
* Deleted records are not counted in reports.
* Reports should use `exit_time` for revenue date.

## Plate Number Normalization

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

These search inputs should match the same vehicle:

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

## Pricing Modes

ParkingManagement MVP supports two pricing modes:

```text
fixed
hourly
```

### Fixed Pricing Example

```text
Bike = PKR 50
Car = PKR 100
```

### Hourly Pricing Example

```text
First 2 hours = PKR 100
Every extra hour = PKR 50
Grace period = 10 minutes
```

Pricing changes affect future exits only.

Old completed records keep their existing fee through `pricing_snapshot`.

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd ParkingManagement
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
```

Activate virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend will run on:

```text
http://localhost:8000
```

API docs will be available at:

```text
http://localhost:8000/docs
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on:

```text
http://localhost:3000
```

### 4. MongoDB Setup

Use local MongoDB during development.

MongoDB URI:

```text
mongodb://localhost:27017
```

Database name:

```text
parkingmanagement
```

## Environment Variables

### Backend `.env`

```env
APP_NAME=ParkingManagement
ENVIRONMENT=development
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=parkingmanagement
JWT_SECRET_KEY=change-this-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Frontend `.env.local`

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## Development Phases

### Phase 0: Project Planning

* Define MVP scope
* Finalize roles
* Finalize collections
* Finalize workflow
* Finalize technology stack

### Phase 1: Repository Setup

* Create monorepo structure
* Initialize Git
* Create base folders
* Add README
* Add docs folder

### Phase 2: Documentation

* Architecture document
* Database document
* API contract
* Workflow document
* Deployment document

### Phase 3: Backend Setup

* FastAPI project structure
* Environment configuration
* MongoDB connection
* Common response format
* Error handling

### Phase 4: Authentication

* User model
* Password hashing
* JWT login
* Current user dependency
* Role-based permissions

### Phase 5: Parking Module

* Vehicle entry
* Vehicle exit
* Search
* Parking history
* Fee calculation

### Phase 6: Admin Modules

* Guard management
* Pricing management
* Dashboard
* Reports
* Settings
* Audit logs

### Phase 7: Frontend Integration

* Login page
* Guard dashboard
* Admin dashboard
* Parking entry screen
* Parking exit screen
* Reports screen
* Settings screen

### Phase 8: Export and OCR

* PDF export
* Excel export
* OCR integration later

### Phase 9: Testing and Deployment

* Unit tests
* API tests
* Docker setup
* VPS deployment

## Git Branch Strategy

Recommended branches:

```text
main
develop

feature/auth
feature/users
feature/parking
feature/pricing
feature/dashboard
feature/reports
feature/settings
feature/audit-logs
feature/ocr
feature/deployment
```

## Coding Principles

Follow these rules from day one:

* Keep routers thin.
* Put business logic in services.
* Use repositories for database operations.
* Validate all input with Pydantic.
* Use async throughout the backend.
* Centralize configuration with environment variables.
* Use JWT for authentication.
* Use role-based authorization.
* Normalize plate numbers before saving and searching.
* Prevent duplicate active vehicles.
* Log important actions.
* Create audit logs for sensitive actions.
* Store pricing snapshot in completed records.
* Store payment inside parking records.
* Keep OCR optional.
* Do not add unnecessary collections in MVP.

## Future Enhancements

Future versions may include:

* OCR plate recognition
* Online payments
* JazzCash integration
* EasyPaisa integration
* Stripe integration
* Receipt printing
* Camera integration
* Boom barrier integration
* RFID cards
* Parking slot map
* Mobile app
* Multi-branch support
* Full SaaS multi-tenancy
* Subscription billing
* AI-powered analytics

## Final Summary

ParkingManagement MVP is a simple but production-ready parking management system.

Core flow:

```text
Entry → Active → Search → Exit → Fee → Cash → Completed
```

Core stack:

```text
Next.js + FastAPI + MongoDB
```

Core roles:

```text
Admin + Guard
```

Core collections:

```text
users
parking_records
pricing_rules
settings
audit_logs
```

The first goal is to build the parking system correctly. Advanced features should be added only after the MVP is stable.