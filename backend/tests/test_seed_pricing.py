from unittest.mock import AsyncMock

import pytest

from scripts.seed_pricing import DEFAULT_PRICING, seed_pricing


@pytest.mark.asyncio
async def test_seed_pricing_creates_bike_and_car_defaults(capsys) -> None:
    repository = AsyncMock()
    repository.find_active_by_vehicle_type.return_value = None
    repository.create_pricing_rule.side_effect = lambda data: data

    created = await seed_pricing(repository)

    assert created == 2
    documents = [
        call.args[0]
        for call in repository.create_pricing_rule.await_args_list
    ]
    assert [document["vehicle_type"] for document in documents] == [
        "bike",
        "car",
    ]
    assert documents[0]["fixed_rate"] == 50
    assert documents[1]["fixed_rate"] == 100
    assert all(document["pricing_type"] == "fixed" for document in documents)
    assert all(document["currency"] == "PKR" for document in documents)
    assert all(document["is_active"] is True for document in documents)
    assert all(document["created_at"].tzinfo is not None for document in documents)
    output = capsys.readouterr().out
    assert "bike pricing created successfully" in output
    assert "car pricing created successfully" in output


@pytest.mark.asyncio
async def test_seed_pricing_is_idempotent_per_vehicle_type(capsys) -> None:
    repository = AsyncMock()
    repository.find_active_by_vehicle_type.side_effect = [
        {"vehicle_type": "bike", "is_active": True},
        {"vehicle_type": "car", "is_active": True},
    ]

    created = await seed_pricing(repository)

    assert created == 0
    repository.create_pricing_rule.assert_not_awaited()
    output = capsys.readouterr().out
    assert "bike pricing already exists" in output
    assert "car pricing already exists" in output


def test_default_pricing_matches_phase_8_prompt() -> None:
    assert DEFAULT_PRICING == {
        "bike": {
            "pricing_type": "fixed",
            "fixed_rate": 50,
        },
        "car": {
            "pricing_type": "fixed",
            "fixed_rate": 100,
        },
    }
