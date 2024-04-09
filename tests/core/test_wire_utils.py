import newsroom.wire.utils as utils


def test_get_picture():
    item = {"type": "text", "associations": {"first": None, "second": {"type": "text"}, "third": {"type": "picture"}}}
    picture = utils.get_picture(item)
    assert picture == item["associations"]["third"]
