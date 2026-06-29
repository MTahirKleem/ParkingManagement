
# ParkingManagement Workflow

## 1. Workflow Overview

ParkingManagement is designed around a simple parking lifecycle:

```text
Vehicle Entry → Active Parking → Vehicle Exit → Fee Calculation → Cash Payment → Completed Record
```

The MVP has two roles:

```text
admin
guard
```

The Guard handles daily parking operations.

The Admin manages users, pricing, reports, settings, and all parking records.

## 2. Main Parking Lifecycle

```text
Vehicle Arrives
       ↓
Guard Logs In
       ↓
Guard Enters Plate Number
       ↓
Guard Selects Vehicle Type
       ↓
System Saves Entry
       ↓
Vehicle Status Becomes Active
       ↓
Vehicle Leaves
       ↓
Guard Searches Plate Number
       ↓
System Shows Parking Details
       ↓
System Calculates Fee
       ↓
Guard Receives Cash
       ↓
Guard Completes Parking Session
       ↓
Vehicle Status Becomes Completed
```

## 3. Guard Workflow

The Guard is responsible for daily parking operations.

### Guard Login Flow

```text
Open application
       ↓
Enter email and password
       ↓
Backend validates credentials
       ↓
JWT token is returned
       ↓
Guard is redirected to Guard Dashboard
```

### Guard Dashboard

Guard dashboard shows:

```text
Active vehicles
Today's entries
Today's exits
Recent entries
```

Guard should not see full revenue analytics in MVP.

## 4. Vehicle Entry Workflow

### Step-by-Step Flow

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
Frontend sends request to backend
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

### Vehicle Entry API

```http
POST /api/v1/parking/entry
```

### Required Fields

```text
plate_number
vehicle_type
```

### Optional Fields

```text
slot
```

### System Generated Fields

```text
normalized_plate_number
entry_time
status = active
created_by
created_at
updated_at
```

### Entry Business Rules

* Plate number is required.
* Vehicle type is required.
* Vehicle type must be `bike` or `car`.
* Entry time is automatic.
* Parking status must be `active`.
* Same active plate number cannot exist twice.
* Plate number must be normalized before saving.
* Guard ID must be stored in `created_by`.
* Audit log must be created with action `VEHICLE_ENTRY_CREATED`.

### Example Entry Request

```json
{
  "plate_number": "LEA-1234",
  "vehicle_type": "bike",
  "slot": "A-12"
}
```

### Example Entry Result

```json
{
  "plate_number": "LEA-1234",
  "normalized_plate_number": "LEA1234",
  "vehicle_type": "bike",
  "slot": "A-12",
  "entry_time": "2026-06-29T10:00:00Z",
  "status": "active"
}
```

## 5. Active Vehicle Workflow

After entry is saved, the vehicle becomes active.

### Active Vehicle State

```text
status = active
exit_time = null
fee = null
payment = null
```

### Guard Can

```text
View active vehicles
Search active vehicles
Open vehicle details
Mark vehicle exit
```

### Admin Can

```text
View active vehicles
Edit record if needed
Delete record if needed
View who created the entry
```

## 6. Vehicle Search Workflow

### Step-by-Step Flow

```text
Guard opens Search screen
       ↓
Guard enters plate number
       ↓
Frontend sends search query
       ↓
Backend normalizes search input
       ↓
Backend searches normalized plate number
       ↓
Backend returns matching records
       ↓
Guard opens vehicle details
```

### Search API

```http
GET /api/v1/parking/search?plate_number=LEA-1234
```

### Plate Normalization Examples

All of these should match the same vehicle:

```text
LEA-1234
LEA 1234
lea1234
LEA1234
```

Normalized value:

```text
LEA1234
```

### Search Business Rules

* Search should use normalized plate number.
* Guard can search active vehicles.
* Guard can search completed vehicles.
* Admin can search all parking records.
* Deleted records should not appear in normal search results.

## 7. Vehicle Exit Workflow

### Step-by-Step Flow

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

### Vehicle Exit API

```http
POST /api/v1/parking/{record_id}/exit
```

### Exit Request

```json
{
  "payment_received": true
}
```

### System Generated Fields

```text
exit_time
duration_minutes
fee
payment
pricing_snapshot
completed_by
updated_at
status = completed
```

### Exit Business Rules

* Record must exist.
* Record must be active.
* Completed record cannot be exited again.
* Exit time is automatic.
* Fee is calculated by the system.
* Payment method is cash only.
* Cash must be marked as received.
* Pricing snapshot must be stored.
* Status becomes `completed`.
* Audit log must be created with action `VEHICLE_EXIT_COMPLETED`.

### Example Completed Payment

```json
{
  "method": "cash",
  "received": true,
  "received_by": "66a000000000000000000002",
  "received_at": "2026-06-29T12:16:00Z"
}
```

## 8. Fee Calculation Workflow

Fee calculation happens only during vehicle exit.

### Step-by-Step Flow

```text
Parking Service receives exit request
       ↓
Parking Service loads active parking record
       ↓
Parking Service sends vehicle type and duration to Pricing Service
       ↓
Pricing Service loads active pricing rule
       ↓
Pricing Service calculates final fee
       ↓
Pricing Service returns fee and pricing snapshot
       ↓
Parking Service saves fee in parking record
```

### Pricing Types

MVP supports:

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

### Fee Rules

* Fee is calculated only at exit time.
* Active vehicles do not have a fee yet.
* Old completed records should not change if pricing changes later.
* Pricing snapshot must be saved in completed parking records.

## 9. Admin Workflow

The Admin manages the complete system.

### Admin Login Flow

```text
Open application
       ↓
Enter admin credentials
       ↓
Backend validates credentials
       ↓
JWT token is returned
       ↓
Admin is redirected to Admin Dashboard
```

### Admin Dashboard

Admin dashboard shows:

```text
Total revenue
Today's revenue
Monthly revenue
Active vehicles
Completed vehicles
Today's entries
Today's exits
Parking occupancy
Revenue by guard
Revenue by vehicle type
Recent transactions
```

## 10. Guard Management Workflow

### Create Guard

```text
Admin opens Users screen
       ↓
Admin clicks Create Guard
       ↓
Admin enters name, email, phone, password
       ↓
Backend checks email uniqueness
       ↓
Backend hashes password
       ↓
Backend creates guard user
       ↓
Backend creates audit log
```

### Update Guard

```text
Admin opens guard profile
       ↓
Admin updates name, phone, or status
       ↓
Backend updates user
       ↓
Backend creates audit log
```

### Delete Guard

```text
Admin selects guard
       ↓
Admin confirms delete
       ↓
Backend sets status = deleted
       ↓
Backend creates audit log
```

### Reset Password

```text
Admin opens guard profile
       ↓
Admin enters new password
       ↓
Backend hashes new password
       ↓
Backend updates password_hash
       ↓
Backend creates audit log
```

## 11. Pricing Workflow

Only Admin can manage pricing.

### Pricing Update Flow

```text
Admin opens Pricing screen
       ↓
Admin selects bike or car pricing
       ↓
Admin selects fixed or hourly pricing
       ↓
Admin enters pricing values
       ↓
Backend validates pricing rule
       ↓
Backend updates pricing
       ↓
Backend creates audit log
```

### Pricing Business Rules

* Only Admin can update pricing.
* Bike and car can have separate pricing rules.
* Fixed pricing requires `fixed_rate`.
* Hourly pricing requires `base_hours`, `base_fee`, and `extra_hour_fee`.
* Pricing changes affect future exits only.
* Completed records keep their old fee using `pricing_snapshot`.

## 12. Reports Workflow

Only Admin can view reports.

### Daily Report Flow

```text
Admin opens Reports screen
       ↓
Admin selects Daily Report
       ↓
Admin selects date
       ↓
Backend fetches completed parking records
       ↓
Backend calculates revenue and counts
       ↓
Frontend displays report
```

### Weekly Report Flow

```text
Admin opens Reports screen
       ↓
Admin selects Weekly Report
       ↓
Admin selects start date and end date
       ↓
Backend fetches completed parking records
       ↓
Backend calculates weekly totals
       ↓
Frontend displays report
```

### Monthly Report Flow

```text
Admin opens Reports screen
       ↓
Admin selects Monthly Report
       ↓
Admin selects month and year
       ↓
Backend fetches completed parking records
       ↓
Backend calculates monthly totals
       ↓
Frontend displays report
```

### Custom Report Flow

```text
Admin opens Reports screen
       ↓
Admin selects start date and end date
       ↓
Backend validates date range
       ↓
Backend fetches completed records
       ↓
Backend calculates report data
       ↓
Frontend displays report
```

### Report Rules

* Reports count only completed records.
* Revenue counts only records with `payment.received = true`.
* Active vehicles are not counted in revenue.
* Deleted records are not counted in reports.
* Reports should use `exit_time` for revenue date.

## 13. Export Workflow

Only Admin can export reports.

### PDF Export

```text
Admin selects report type
       ↓
Admin clicks Export PDF
       ↓
Backend generates report data
       ↓
Backend creates PDF file
       ↓
Backend returns downloadable file
       ↓
Backend creates audit log
```

### Excel Export

```text
Admin selects report type
       ↓
Admin clicks Export Excel
       ↓
Backend generates report data
       ↓
Backend creates Excel file
       ↓
Backend returns downloadable file
       ↓
Backend creates audit log
```

## 14. Settings Workflow

Only Admin can update settings.

### Settings Update Flow

```text
Admin opens Settings screen
       ↓
Admin updates parking name, address, phone, logo, currency, capacity, footer
       ↓
Backend validates settings
       ↓
Backend updates settings document
       ↓
Backend creates audit log
```

### Settings Used In

```text
Dashboard
Reports
PDF exports
Excel exports
Receipt later
Parking occupancy calculation
```

## 15. Audit Log Workflow

Audit logs are created automatically for important actions.

### Actions That Create Audit Logs

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
PRICING_RULE_UPDATED
SETTINGS_UPDATED
REPORT_GENERATED
EXPORT_PDF_GENERATED
EXPORT_EXCEL_GENERATED
```

### Audit Rules

* Audit logs are append-only.
* Audit logs should not be edited.
* Admin can view audit logs.
* Guard cannot view audit logs.
* Passwords and JWT tokens must never be logged.

## 16. OCR Workflow Later

OCR is not part of the first implementation.

Manual entry must always work.

### Future OCR Flow

```text
Guard opens Vehicle Entry screen
       ↓
Guard uploads vehicle image
       ↓
Frontend sends image to OCR API
       ↓
Backend sends image to OCR service
       ↓
OCR service returns plate number and confidence
       ↓
Frontend shows detected plate
       ↓
Guard confirms or corrects plate number
       ↓
Guard saves vehicle entry
```

### OCR Rules

* OCR is optional.
* OCR should not automatically create entry.
* Guard must confirm or correct OCR result.
* OCR result can be stored inside parking record.
* Manual plate entry must always remain available.

## 17. Complete MVP User Journey

### Guard Journey

```text
Login
       ↓
View Guard Dashboard
       ↓
Add Vehicle Entry
       ↓
Search Active Vehicle
       ↓
Complete Vehicle Exit
       ↓
Receive Cash
       ↓
View Today’s Entries and Exits
```

### Admin Journey

```text
Login
       ↓
View Admin Dashboard
       ↓
Manage Guards
       ↓
Manage Pricing
       ↓
View Parking Records
       ↓
Generate Reports
       ↓
Export PDF or Excel
       ↓
Update Settings
       ↓
View Audit Logs
```

## 18. Workflow Summary

ParkingManagement MVP should keep the workflow simple:

```text
Entry → Active → Search → Exit → Fee → Cash → Completed
```

The most important workflow rules are:

* Guard can create entry.
* Guard can complete exit.
* Fee is automatic.
* Cash payment is stored in parking record.
* Admin manages guards, pricing, reports, and settings.
* OCR is future optional helper only.

