import pytest
from unittest.mock import patch
from newsroom.assets.utils import get_content_disposition


@pytest.fixture(autouse=True)
def mock_guess_media_extension():
    with patch("newsroom.assets.utils.guess_media_extension", return_value=".pdf") as mock:
        yield mock


def test_content_disposition_with_extension():
    filename = "example.pdf"
    disposition = get_content_disposition(filename)
    assert disposition == 'attachment; filename="example.pdf"'


def test_content_disposition_without_extension_using_metadata():
    filename = "example"
    metadata = {"contentType": "application/pdf"}
    disposition = get_content_disposition(filename, metadata)
    assert disposition == 'attachment; filename="example.pdf"'


def test_content_disposition_without_filename():
    disposition = get_content_disposition(None)
    assert disposition == "inline"


def test_content_disposition_with_unsafe_filename():
    filename = "../path/to/example.pdf"
    disposition = get_content_disposition(filename)
    assert disposition == 'attachment; filename="path_to_example.pdf"'
