from fast_header.etag import ETag


def test_strong():
    assert str(ETag(value="a")) == "a"


def test_week():
    assert str(ETag(value="a", weak=True)) == f'W/"a"'
