from datetime import datetime, timezone

from bson import ObjectId
from fastapi.testclient import TestClient

from app.api.v1.parking import get_parking_service
from app.core.constants import UserRoles
from app.core.permissions import get_current_user
from app.main import app


def make_user(role):
    return {
        "_id": ObjectId(),
        "name": "Actor",
        "email": f"{role}@example.com",
        "role": role,
        "status": "active",
    }


def record(record_id=None, status="active"):
    now = datetime(2026, 6, 29, 10, 0, tzinfo=timezone.utc)
    return {
        "id": record_id or str(ObjectId()),
        "plate_number": "LEA-1234",
        "normalized_plate_number": "LEA1234",
        "vehicle_type": "bike",
        "slot": "A-12",
        "entry_time": now,
        "exit_time": now if status == "completed" else None,
        "status": status,
        "duration_minutes": 60 if status == "completed" else None,
        "fee": 50 if status == "completed" else None,
        "currency": "PKR",
        "payment": (
            {
                "method": "cash",
                "received": True,
                "received_by": str(ObjectId()),
                "received_by_name": "Exit Guard",
                "received_at": now,
            }
            if status == "completed"
            else None
        ),
        "pricing_snapshot": (
            {
                "pricing_rule_id": str(ObjectId()),
                "pricing_type": "fixed",
                "fixed_rate": 50,
                "base_hours": None,
                "base_fee": None,
                "extra_hour_fee": None,
                "grace_minutes": 0,
            }
            if status == "completed"
            else None
        ),
        "ocr": None,
        "notes": None,
        "created_by": str(ObjectId()),
        "created_by_name": "Entry Guard",
        "completed_by": None,
        "completed_by_name": None,
        "updated_by": None,
        "created_at": now,
        "updated_at": now,
    }


class FakeParkingService:
    async def create_entry(self, payload, current_user, request_context):
        return record()

    async def complete_exit(
        self, record_id, payload, current_user, request_context
    ):
        return record(record_id, status="completed")

    async def get_active_vehicles(self, filters):
        return {
            "data": [record()],
            "pagination": {
                "page": filters["page"],
                "limit": filters["limit"],
                "total": 1,
                "pages": 1,
            },
        }

    async def get_history(self, filters):
        return {
            "data": [record(status="completed")],
            "pagination": {
                "page": filters["page"],
                "limit": filters["limit"],
                "total": 1,
                "pages": 1,
            },
        }

    async def search_records(self, plate_number, status):
        return [record(status=status or "active")]

    async def get_record_by_id(self, record_id):
        return record(record_id)

    async def update_record(
        self, record_id, payload, current_user, request_context
    ):
        result = record(record_id)
        result.update(payload.model_dump(exclude_unset=True))
        if payload.plate_number:
            result["normalized_plate_number"] = "LEA9999"
        return result

    async def delete_record(self, record_id, current_user, request_context):
        return {"id": record_id, "status": "deleted"}


def make_client(user=None):
    app.dependency_overrides[get_parking_service] = (
        lambda: FakeParkingService()
    )
    if user is not None:
        app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app, raise_server_exceptions=False)


def teardown_function():
    app.dependency_overrides.clear()


def test_openapi_contains_all_phase_8_routes_and_previous_routes() -> None:
    paths = app.openapi()["paths"]
    expected = {
        ("/api/v1/parking/entry", "post"),
        ("/api/v1/parking/{record_id}/exit", "post"),
        ("/api/v1/parking/active", "get"),
        ("/api/v1/parking/history", "get"),
        ("/api/v1/parking/search", "get"),
        ("/api/v1/parking/{record_id}", "get"),
        ("/api/v1/parking/{record_id}", "put"),
        ("/api/v1/parking/{record_id}", "delete"),
        ("/api/v1/auth/login", "post"),
        ("/api/v1/users", "get"),
        ("/api/v1/health", "get"),
    }

    assert all(method in paths[path] for path, method in expected)


def test_admin_can_use_all_parking_routes() -> None:
    client = make_client(make_user(UserRoles.ADMIN))
    record_id = str(ObjectId())

    responses = [
        client.post(
            "/api/v1/parking/entry",
            json={
                "plate_number": "LEA-1234",
                "vehicle_type": "bike",
                "slot": "A-12",
            },
        ),
        client.post(
            f"/api/v1/parking/{record_id}/exit",
            json={"payment_received": True},
        ),
        client.get("/api/v1/parking/active?page=1&limit=20"),
        client.get(
            "/api/v1/parking/history?status=completed&start_date=2026-06-01&end_date=2026-06-29"
        ),
        client.get(
            "/api/v1/parking/search?plate_number=LEA-1234&status=active"
        ),
        client.get(f"/api/v1/parking/{record_id}"),
        client.put(
            f"/api/v1/parking/{record_id}",
            json={"plate_number": "LEA-9999", "notes": "Corrected"},
        ),
        client.delete(f"/api/v1/parking/{record_id}"),
    ]

    assert [response.status_code for response in responses] == [
        201,
        200,
        200,
        200,
        200,
        200,
        200,
        200,
    ]
    assert all(response.json()["success"] is True for response in responses)
    assert responses[1].json()["data"]["payment"]["method"] == "cash"
    assert (
        responses[1].json()["data"]["payment"]["received_by_name"]
        == "Exit Guard"
    )
    assert responses[0].json()["data"]["created_by_name"] == "Entry Guard"
    assert responses[7].json()["data"]["status"] == "deleted"


def test_guard_can_operate_but_cannot_update_or_delete() -> None:
    client = make_client(make_user(UserRoles.GUARD))
    record_id = str(ObjectId())

    assert (
        client.post(
            "/api/v1/parking/entry",
            json={"plate_number": "ABC-1", "vehicle_type": "car"},
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/api/v1/parking/{record_id}/exit",
            json={"payment_received": True},
        ).status_code
        == 200
    )
    assert client.get("/api/v1/parking/active").status_code == 200
    assert client.get("/api/v1/parking/history").status_code == 200
    assert (
        client.get("/api/v1/parking/search?plate_number=ABC-1").status_code
        == 200
    )
    assert client.get(f"/api/v1/parking/{record_id}").status_code == 200

    update = client.put(
        f"/api/v1/parking/{record_id}", json={"slot": "B-1"}
    )
    delete = client.delete(f"/api/v1/parking/{record_id}")
    assert (update.status_code, update.json()["error_code"]) == (
        403,
        "FORBIDDEN",
    )
    assert (delete.status_code, delete.json()["error_code"]) == (
        403,
        "FORBIDDEN",
    )


def test_missing_token_and_invalid_requests_use_standard_errors() -> None:
    client = make_client()

    missing = client.get("/api/v1/parking/active")
    client = make_client(make_user(UserRoles.ADMIN))
    invalid_entry = client.post(
        "/api/v1/parking/entry",
        json={"plate_number": "", "vehicle_type": "truck"},
    )
    invalid_exit = client.post(
        f"/api/v1/parking/{ObjectId()}/exit",
        json={"payment_received": False},
    )
    invalid_pagination = client.get("/api/v1/parking/active?limit=101")
    invalid_dates = client.get(
        "/api/v1/parking/history"
        "?start_date=2026-06-30&end_date=2026-06-01"
    )

    assert (missing.status_code, missing.json()["error_code"]) == (
        401,
        "UNAUTHORIZED",
    )
    for response in (
        invalid_entry,
        invalid_exit,
        invalid_pagination,
        invalid_dates,
    ):
        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"
