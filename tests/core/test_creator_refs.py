from bson import ObjectId

from newsroom.tests.users import test_login_succeeds_for_admin

from tests.core.utils import create_entries_for, find_one_by_id, update_entries_for


async def test_update_user_with_deleted_creator_ref_succeeds(client):
    await test_login_succeeds_for_admin(client)

    creator_id = (
        await create_entries_for(
            "users",
            [
                {
                    "email": f"creator-{ObjectId()}@example.com",
                    "first_name": "Creator",
                    "last_name": "User",
                    "user_type": "public",
                    "is_enabled": True,
                    "is_approved": True,
                    "is_validated": True,
                }
            ],
        )
    )[0]

    user_id = (
        await create_entries_for(
            "users",
            [
                {
                    "email": f"target-{ObjectId()}@example.com",
                    "first_name": "Target",
                    "last_name": "User",
                    "user_type": "public",
                    "is_enabled": True,
                    "is_approved": True,
                    "is_validated": True,
                    "version_creator": creator_id,
                }
            ],
        )
    )[0]

    resp = await client.delete(f"/users/{creator_id}")
    assert resp.status_code == 200
    assert await find_one_by_id("users", creator_id) is None

    original_user = await find_one_by_id("users", user_id)
    assert original_user is not None

    await update_entries_for("users", user_id, {"last_name": "Updated"}, original_user)

    updated_user = await find_one_by_id("users", user_id)
    assert updated_user["last_name"] == "Updated"
    assert updated_user["version_creator"] == creator_id


async def test_update_company_with_deleted_creator_ref_succeeds(client):
    await test_login_succeeds_for_admin(client)

    creator_id = (
        await create_entries_for(
            "users",
            [
                {
                    "email": f"creator-{ObjectId()}@example.com",
                    "first_name": "Creator",
                    "last_name": "User",
                    "user_type": "public",
                    "is_enabled": True,
                    "is_approved": True,
                    "is_validated": True,
                }
            ],
        )
    )[0]

    company_id = (
        await create_entries_for(
            "companies",
            [
                {
                    "name": f"Company {ObjectId()}",
                    "contact_name": "Original",
                    "is_enabled": True,
                    "version_creator": creator_id,
                }
            ],
        )
    )[0]

    resp = await client.delete(f"/users/{creator_id}")
    assert resp.status_code == 200
    assert await find_one_by_id("users", creator_id) is None

    original_company = await find_one_by_id("companies", company_id)
    assert original_company is not None

    await update_entries_for("companies", company_id, {"contact_name": "Updated"}, original_company)

    updated_company = await find_one_by_id("companies", company_id)
    assert updated_company["contact_name"] == "Updated"
    assert updated_company["version_creator"] == creator_id
