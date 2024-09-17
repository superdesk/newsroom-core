import pytest
from pydantic_core import PydanticCustomError
from pydantic import BaseModel
from unittest.mock import AsyncMock, patch, MagicMock
from newsroom.core.resources.validators import validate_multi_field_iunique_value_async


class TestModel(BaseModel):
    id: str
    name: str
    product_type: str | None


@pytest.fixture
def mock_app():
    return MagicMock()


@pytest.fixture
def mock_collection():
    return AsyncMock()


@pytest.mark.asyncio
async def test_validate_unique_combination_no_errors(mock_app, mock_collection):
    with patch("newsroom.core.resources.validators.get_current_async_app", return_value=mock_app):
        mock_app.mongo.get_collection_async.return_value = mock_collection
        mock_collection.find_one.return_value = None

        validator = validate_multi_field_iunique_value_async("navigations", ["name", "product_type"]).func
        item = TestModel(id="123", name="Sports", product_type="wire")

        await validator(item, item.name)
        mock_collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_validate_unique_combination_existent_registry(mock_app, mock_collection):
    with patch("newsroom.core.resources.validators.get_current_async_app", return_value=mock_app):
        mock_app.mongo.get_collection_async.return_value = mock_collection
        mock_collection.find_one.return_value = {"_id": "456"}

        validator = validate_multi_field_iunique_value_async("navigations", ["name", "product_type"]).func
        item = TestModel(id="123", name="Sports", product_type="wire")

        with pytest.raises(PydanticCustomError):
            await validator(item, item.name)
        mock_collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_validate_skip_if_field_is_none(mock_app, mock_collection):
    with patch("newsroom.core.resources.validators.get_current_async_app", return_value=mock_app):
        mock_app.mongo.get_collection_async.return_value = mock_collection

        validator = validate_multi_field_iunique_value_async("navigations", ["name", "product_type"]).func
        item = TestModel(id="123", name="Sports", product_type=None)

        await validator(item, item.name)
        mock_collection.find_one.assert_not_called()
