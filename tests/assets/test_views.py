import pytest
from unittest import mock

"""
Test "dot image" generated with PIL

image = Image.new('RGBA', (1, 1), (0, 0, 0, 255)) # RGBA: black dot
byte_arr = io.BytesIO()
image.save(byte_arr, format='PNG')
image_content = byte_arr.getvalue()
"""
TEST_PNG_BLACK_DOT = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc```\xf8\x0f\x00\x01\x04\x01\x00_\xe5\xc3K\x00\x00\x00\x00IEND\xaeB`\x82"


async def save_black_dot_image(app):
    media_id = await app.media_async.put(TEST_PNG_BLACK_DOT, content_type="image/png", filename="image.png")
    return media_id


@pytest.fixture(autouse=True)
def mock_valid_session():
    with mock.patch("newsroom.assets.views.is_valid_session", return_value=True):
        yield


async def test_valid_media_request(client_async, app):
    media_id = await save_black_dot_image(app)
    response = await client_async.get(f"/assets/{media_id}")

    assert response.status_code == 200
    assert response.content_type == "image/png"
    assert "Content-Disposition" in response.headers


def test_media_not_found(client):
    media_id = "nonexistent_media_id"
    response = client.get(f"/assets/{media_id}")
    assert response.status_code == 404


async def test_filename_in_response_header(client_async, app):
    media_id = await app.media_async.put(b"Plain text content", content_type="plain/text", filename="testfile.txt")

    response = await client_async.get(f"/assets/{media_id}?filename=testfile.txt")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == 'attachment; filename="testfile.txt"'
