import pytest
from unittest.mock import patch, Mock
from werkzeug.datastructures import FileStorage
from newsroom.assets.utils import get_content_disposition, generate_response_headers, save_file_and_get_url


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


def test_generate_response_headers():
    media_file = Mock()
    media_file.filename = "testfile.pdf"
    media_file.upload_date = "Wed, 21 Oct 2015 07:28:00 GMT"
    media_file.content_type = "application/pdf"
    media_file.metadata = {"contentType": "application/pdf"}

    expected_headers = [
        ("Content-Disposition", 'attachment; filename="testfile.pdf"'),
        ("Last-Modified", "Wed, 21 Oct 2015 07:28:00 GMT"),
        ("Cache-Control", "max-age=604800, public"),
        ("Content-Type", "application/pdf"),
    ]

    headers = generate_response_headers(media_file)
    assert headers == expected_headers


async def test_save_file_and_get_url_successful():
    file_storage = FileStorage(filename="testfile.txt", content_type="text/plain")

    path_secure_filename = "newsroom.assets.utils.secure_filename"
    path_url_for = "newsroom.assets.utils.url_for"

    with patch(path_secure_filename, return_value="testfile.txt") as mock_secure:
        with patch(path_url_for, return_value="/assets/testfile.txt") as mock_url_for:
            result = await save_file_and_get_url(file_storage)

            assert result == "/assets/testfile.txt"
            mock_secure.assert_called_once_with("testfile.txt")
            mock_url_for.assert_called_once_with("assets.download_file", media_id="testfile.txt")
