from unittest.mock import AsyncMock

import pytest

from app.core.constants import UserRoles, UserStatus
from app.core.security import verify_password
from scripts.seed_admin import DEFAULT_ADMIN_EMAIL, seed_admin


@pytest.mark.asyncio
async def test_seed_admin_does_not_duplicate_existing_admin(capsys) -> None:
    repository = AsyncMock()
    repository.find_by_email.return_value = {"email": DEFAULT_ADMIN_EMAIL}

    created = await seed_admin(repository)

    assert created is False
    repository.create_user.assert_not_awaited()
    assert "already exists" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_seed_admin_creates_required_hashed_document(capsys) -> None:
    repository = AsyncMock()
    repository.find_by_email.return_value = None
    repository.create_user.side_effect = lambda data: data

    created = await seed_admin(repository)

    document = repository.create_user.await_args.args[0]
    assert created is True
    assert document["email"] == DEFAULT_ADMIN_EMAIL
    assert document["role"] == UserRoles.ADMIN
    assert document["status"] == UserStatus.ACTIVE
    assert document["created_by"] is None
    assert verify_password("Admin@123", document["password_hash"])
    assert "created successfully" in capsys.readouterr().out
