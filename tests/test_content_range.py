from fast_header import ContentRange, Range


def test_base():
    cr = ContentRange(
        range=Range(start=0,stop=20),
        size=30
    )
    assert str(cr) == "bytes 0-20/30"

def test_empty_size():
    cr = ContentRange(
        range=Range(start=0,stop=20),
    )
    assert str(cr) == "bytes 0-20/*"

def test_zero_size():
    cr = ContentRange(
        range=Range(start=0,stop=20),
        size=0
    )
    assert str(cr) == "bytes 0-20/0"

def test_empty_range():
    cr = ContentRange(
        size=20
    )
    assert str(cr) == "bytes */20"


def test_parse():
    cr = ContentRange.parse("bytes 0-20/30")
    assert cr.unit == "bytes"
    assert cr.range is not None
    assert cr.range.start == 0
    assert cr.range.stop == 20
    assert cr.size == 30

def test_parse_empty_size():
    cr = ContentRange.parse("bytes 10-20/*")
    assert cr.unit == "bytes"
    assert cr.range is not None
    assert cr.range.start == 10
    assert cr.range.stop == 20
    assert cr.size is None

def test_parse_empty_range():
    cr = ContentRange.parse("bytes */30")
    assert cr.unit == "bytes"
    assert cr.range is None
    assert cr.size == 30
