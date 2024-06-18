import pytest
from fast_header.content_type import ContentType


invalidTypes = [
    " ",
    "null",
    "undefined",
    "/",
    "text / plain",
    "text/;plain",
    'text/"plain"',
    "text/p£ain",
    "text/(plain)",
    "text/@plain",
    "text/plain,wrong",
]


def test_parse_basic():
    ct = ContentType.parse("text/html")
    assert ct.type == "text/html"


def test_suffix():
    ct = ContentType.parse("image/svg+xml")
    assert ct.type == "image/svg+xml"


def test_surrounding():
    ct = ContentType.parse(" text/html ")
    assert ct.type == "text/html"


def test_params():
    ct = ContentType.parse("text/html; charset=utf-8; foo=bar")
    assert ct.type == "text/html"
    assert ct.parameters == {"charset": "utf-8", "foo": "bar"}


def test_lws():
    ct = ContentType.parse("text/html ; charset=utf-8 ; foo=bar")
    assert ct.type == "text/html"
    assert ct.parameters == {"charset": "utf-8", "foo": "bar"}


def test_lower_case():
    ct = ContentType.parse("IMAGE/SVG+XML")
    assert ct.type == "image/svg+xml"


def test_lower_case_parameter_name():
    ct = ContentType.parse("text/html; Charset=UTF-8")
    assert ct.type == "text/html"
    assert ct.parameters == {"charset": "UTF-8"}


def test_unquote():
    ct = ContentType.parse('text/html; charset="UTF-8"')
    assert ct.type == "text/html"
    assert ct.parameters == {"charset": "UTF-8"}


def test_unquote_escapes():
    ct = ContentType.parse('text/html; charset = "UT\\F-\\\\\\"8\\""')
    assert ct.type == "text/html"
    assert ct.parameters == {"charset": 'UTF-\\"8"'}


def test_balanced_quotes():
    ct = ContentType.parse('text/html; param="charset=\\"utf-8\\"; foo=bar"; bar=foo')
    assert ct.type == "text/html"
    assert ct.parameters == {"param": 'charset="utf-8"; foo=bar', "bar": "foo"}


def test_invalid_types():
    for t in invalidTypes:
        with pytest.raises(Exception) as e_info:
            ContentType.parse(t)


def test_invalid_param():
    with pytest.raises(Exception) as e_info:
        ContentType.parse('text/plain; foo="bar')
    with pytest.raises(Exception) as e_info:
        ContentType.parse("text/plain; profile=http://localhost; foo=bar")
    with pytest.raises(Exception) as e_info:
        ContentType.parse("text/plain; profile=http://localhost")


def test_basic_format():
    ct = ContentType(type="text/html")
    assert str(ct) == "text/html"


def test_suffix2():
    ct = ContentType(type="image/svg+xml")
    assert str(ct) == "image/svg+xml"


def test_charset():
    ct = ContentType(type="text/html", charset="utf-8")
    assert str(ct) == "text/html; charset=utf-8"


def test_quotes():
    ct = ContentType(type="text/html", foo='bar or "baz"')
    assert str(ct) == 'text/html; foo="bar or \\"baz\\""'


def test_empty():
    ct = ContentType(type="text/html", foo="")
    assert str(ct) == 'text/html; foo=""'


def test_multiple_params():
    ct = ContentType(type="text/html", charset="utf-8", foo="bar", bar="baz")
    assert str(ct) == "text/html; bar=baz; charset=utf-8; foo=bar"
