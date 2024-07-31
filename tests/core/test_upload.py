def test_valid_media_request(client, app):
    media_id = app.media.put(b"This is the content", content_type="plain/text")

    response = client.get(f"/assets/{media_id}")
    assert response.status_code == 200
    assert response.content_type == "plain/text"
    assert "Content-Disposition" in response.headers


def test_media_not_found(client):
    media_id = "nonexistent_media_id"
    response = client.get(f"/assets/{media_id}")
    assert response.status_code == 404


def test_filename_in_response_header(client, app):
    media_id = app.media.put(b"File content", content_type="plain/text")

    response = client.get(f"/assets/{media_id}?filename=testfile.txt")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == 'attachment; filename="testfile.txt"'


def test_content_disposition_inline(client, app):
    media_id = app.media.put(b"Sample content", content_type="image/jpeg")

    response = client.get(f"/assets/{media_id}")
    assert response.status_code == 200
    assert "inline" in response.headers["Content-Disposition"]
