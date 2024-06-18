from pydantic import ValidationError
import pytest
from fast_header.content_disposition import ContentDisposition


def test_empty():
    cd = ContentDisposition()
    assert cd.type == "attachment"


def test_filename():
    cd = ContentDisposition(filename="plans.pdf")
    assert str(cd) == 'attachment; filename="plans.pdf"'


def test_basename():
    cd = ContentDisposition(filename="/path/to/plans.pdf")
    assert str(cd) == 'attachment; filename="plans.pdf"'


def test_quote():
    cd = ContentDisposition(filename='the "plans".pdf')
    assert str(cd) == 'attachment; filename="the \\"plans\\".pdf"'


def test_iso_8859():
    cd = ContentDisposition(filename="«plans».pdf")
    assert str(cd) == 'attachment; filename="«plans».pdf"'


def test_escape():
    cd = ContentDisposition(filename='the "plans" (1µ).pdf')
    assert str(cd) == 'attachment; filename="the \\"plans\\" (1µ).pdf"'


def test_unicode():
    cd = ContentDisposition(filename="планы.pdf")
    assert (
        str(cd)
        == "attachment; filename=\"?????.pdf\"; filename*=UTF-8''%D0%BF%D0%BB%D0%B0%D0%BD%D1%8B.pdf"
    )


def test_fallback():
    cd = ContentDisposition(filename="£ and € rates.pdf")
    assert (
        str(cd)
        == "attachment; filename=\"£ and ? rates.pdf\"; filename*=UTF-8''%C2%A3%20and%20%E2%82%AC%20rates.pdf"
    )
    cd = ContentDisposition(filename="€ rates.pdf")
    assert (
        str(cd)
        == "attachment; filename=\"? rates.pdf\"; filename*=UTF-8''%E2%82%AC%20rates.pdf"
    )


def test_special_chars():
    cd = ContentDisposition(filename="€'*%().pdf")
    assert (
        str(cd)
        == "attachment; filename=\"?'*%().pdf\"; filename*=UTF-8''%E2%82%AC%27%2A%25%28%29.pdf"
    )


def test_hex():
    cd = ContentDisposition(filename="the%20plans.pdf")
    assert (
        str(cd)
        == "attachment; filename=\"the%20plans.pdf\"; filename*=UTF-8''the%2520plans.pdf"
    )


def test_unicode2():
    cd = ContentDisposition(filename="€%20£.pdf")
    assert (
        str(cd)
        == "attachment; filename=\"?%20£.pdf\"; filename*=UTF-8''%E2%82%AC%2520%C2%A3.pdf"
    )


def test_fallback_false():
    cd = ContentDisposition(filename="£ and € rates.pdf", fallback=False)
    assert (
        str(cd) == "attachment; filename*=UTF-8''%C2%A3%20and%20%E2%82%AC%20rates.pdf"
    )


def test_ISO_8859():
    cd = ContentDisposition(filename="£ rates.pdf", fallback=False)
    assert str(cd) == 'attachment; filename="£ rates.pdf"'


def test_fallback_true():
    cd = ContentDisposition(filename="£ and € rates.pdf", fallback=True)
    assert (
        str(cd)
        == "attachment; filename=\"£ and ? rates.pdf\"; filename*=UTF-8''%C2%A3%20and%20%E2%82%AC%20rates.pdf"
    )


def test_ISO_8859_fallback():
    cd = ContentDisposition(filename="£ rates.pdf", fallback=True)
    assert str(cd) == 'attachment; filename="£ rates.pdf"'


def test_str_fallback():
    cd = ContentDisposition(
        filename="£ and € rates.pdf", fallback="£ and EURO rates.pdf"
    )
    assert (
        str(cd)
        == "attachment; filename=\"£ and EURO rates.pdf\"; filename*=UTF-8''%C2%A3%20and%20%E2%82%AC%20rates.pdf"
    )


def test_str_fallback_ISO_8859():
    cd = ContentDisposition(filename='"£ rates".pdf', fallback="£ rates.pdf")
    assert (
        str(cd)
        == "attachment; filename=\"£ rates.pdf\"; filename*=UTF-8''%22%C2%A3%20rates%22.pdf"
    )


def test_equal():
    cd = ContentDisposition(filename="plans.pdf", fallback="plans.pdf")
    assert str(cd) == 'attachment; filename="plans.pdf"'


def test_basename_fallback():
    cd = ContentDisposition(filename="€ rates.pdf", fallback="/path/to/EURO rates.pdf")
    assert (
        str(cd)
        == "attachment; filename=\"EURO rates.pdf\"; filename*=UTF-8''%E2%82%AC%20rates.pdf"
    )


def test_nothing():
    cd = ContentDisposition(fallback="plans.pdf")
    assert str(cd) == "attachment"


def test_type():
    cd = ContentDisposition(type="inline")
    assert str(cd) == "inline"


def test_parse():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('"attachment"')


def test_trailing():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment;")


def test_attachment():
    cd = ContentDisposition.parse("attachment")
    assert cd.type == "attachment"


def test_inline():
    cd = ContentDisposition.parse("inline")
    assert cd.type == "inline"


def test_form_data():
    cd = ContentDisposition.parse("form-data")
    assert cd.type == "form-data"


def test_attachment_trailing_lws():
    cd = ContentDisposition.parse("attachment \t ")
    assert cd.type == "attachment"


def test_normalize():
    cd = ContentDisposition.parse("ATTACHMENT")
    assert cd.type == "attachment"


def test_trailing_semicolon():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('attachment; filename="rates.pdf";')


def test_invalid_parameter():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('attachment; filename@="rates.pdf"')


def test_missing_parameter():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=")


def test_invalid_parameter_value():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=trolly,trains")


def test_invalid_parameter2():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=total/; foo=bar")


def test_duplicate_parameters():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=foo; filename=bar")


def test_missing_type():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('filename="plans.pdf"')
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('; filename="plans.pdf"')


def test_lowercase_parameter():
    cd = ContentDisposition.parse('attachment; FILENAME="plans.pdf"')
    assert cd.type == "attachment"
    assert cd.filename == "plans.pdf"


def test_with_parameter():
    cd = ContentDisposition.parse('attachment; filename="plans.pdf"')
    assert cd.type == "attachment"
    assert cd.filename == "plans.pdf"


def test_unescape_quoted_value():
    cd = ContentDisposition.parse('attachment; filename="the \\"plans\\".pdf"')
    assert cd.type == "attachment"
    assert cd.filename == 'the "plans".pdf'


def test_all_parameters():
    cd = ContentDisposition.parse('attachment; filename="plans.pdf"; foo=bar')
    assert cd.type == "attachment"
    assert cd.filename == "plans.pdf"
    assert cd.__pydantic_extra__ is not None
    assert cd.__pydantic_extra__["foo"] == "bar"


def test_lws():
    cd = ContentDisposition.parse('attachment;filename="plans.pdf" \t;    \t\t foo=bar')
    assert cd.type == "attachment"
    assert cd.filename == "plans.pdf"
    assert cd.__pydantic_extra__ is not None
    assert cd.__pydantic_extra__["foo"] == "bar"


def test_parse_filename():
    cd = ContentDisposition.parse("attachment; filename=plans.pdf")
    assert cd.type == "attachment"
    assert cd.filename == "plans.pdf"


def test_ISO_8859_1():
    cd = ContentDisposition.parse('attachment; filename="£ rates.pdf"')
    assert cd.type == "attachment"
    assert cd.filename == "£ rates.pdf"


def test_invalid():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse(
            "attachment; filename*=\"UTF-8''%E2%82%AC%20rates.pdf\""
        )


def test_utf8():
    cd = ContentDisposition.parse("attachment; filename*=UTF-8''%E2%82%AC%20rates.pdf")
    assert cd.type == "attachment"
    assert cd.filename == "€ rates.pdf"


def test_utf82():
    cd = ContentDisposition.parse("attachment; filename*=UTF-8''%E4%20rates.pdf")
    assert cd.type == "attachment"
    assert cd.filename == "\ufffd rates.pdf"


def test_ISO_8859_extended():
    cd = ContentDisposition.parse("attachment; filename*=ISO-8859-1''%A3%20rates.pdf")
    assert cd.type == "attachment"
    assert cd.filename == "£ rates.pdf"

    cd = ContentDisposition.parse("attachment; filename*=ISO-8859-1''%82%20rates.pdf")
    assert cd.type == "attachment"
    assert cd.filename == "? rates.pdf"


def test_case_sensitive():
    cd = ContentDisposition.parse("attachment; filename*=utf-8''%E2%82%AC%20rates.pdf")
    assert cd.type == "attachment"
    assert cd.filename == "€ rates.pdf"


def test_invalid_charset():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename*=ISO-8859-2''%A4%20rates.pdf")


def test_embedded_language():
    cd = ContentDisposition.parse(
        "attachment; filename*=UTF-8'en'%E2%82%AC%20rates.pdf"
    )
    assert cd.type == "attachment"
    assert cd.filename == "€ rates.pdf"


def test_extended():
    cd = ContentDisposition.parse(
        "attachment; filename=\"EURO rates.pdf\"; filename*=UTF-8''%E2%82%AC%20rates.pdf"
    )
    assert cd.type == "attachment"
    assert cd.filename == "€ rates.pdf"

    cd = ContentDisposition.parse(
        "attachment; filename*=UTF-8''%E2%82%AC%20rates.pdf; filename=\"EURO rates.pdf\""
    )
    assert cd.type == "attachment"
    assert cd.filename == "€ rates.pdf"


def test_tc_2231_inline():
    cd = ContentDisposition.parse("inline")
    assert cd.type == "inline"
    assert cd.parameters == {}


def test_invalid_inline():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('"inline"')


def test_inline_filename():
    cd = ContentDisposition.parse('inline; filename="foo.html"')
    assert cd.type == "inline"
    assert cd.parameters == {"filename": "foo.html"}


def test_inline_not_attachment():
    cd = ContentDisposition.parse('inline; filename="Not an attachment!"')
    assert cd.type == "inline"
    assert cd.parameters == {"filename": "Not an attachment!"}


def test_inline_foo():
    cd = ContentDisposition.parse('inline; filename="foo.pdf"')
    assert cd.type == "inline"
    assert cd.parameters == {"filename": "foo.pdf"}


def test_parse_attachment():
    cd = ContentDisposition.parse("attachment")
    assert cd.type == "attachment"
    assert cd.parameters == {}


def test_invalid_attachment():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('"attachment"')


def test_parse_ignore_case():
    cd = ContentDisposition.parse("ATTACHMENT")
    assert cd.type == "attachment"
    assert cd.parameters == {}


def test_parse_foo_html():
    cd = ContentDisposition.parse('attachment; filename="foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html"}


def test_parse_b():
    cd = ContentDisposition.parse('attachment; filename="0000000000111111111122222"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "0000000000111111111122222"}


def test_parse_b2():
    cd = ContentDisposition.parse(
        'attachment; filename="00000000001111111111222222222233333"'
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "00000000001111111111222222222233333"}


def test_parse_b3():
    cd = ContentDisposition.parse('attachment; filename="f\\oo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html"}


def test_parse_quoting():
    cd = ContentDisposition.parse('attachment; filename="\\"quoting\\" tested.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": '"quoting" tested.html'}


def test_parse_semicolon():
    cd = ContentDisposition.parse('attachment; filename="Here\'s a semicolon;.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "Here's a semicolon;.html"}


def test_parse_4():
    cd = ContentDisposition.parse('attachment; foo="bar"; filename="foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html", "foo": "bar"}


def test_parse_5():
    cd = ContentDisposition.parse('attachment; foo="\\"\\\\";filename="foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html", "foo": '"\\'}


def test_parse_6():
    cd = ContentDisposition.parse('attachment; FILENAME="foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html"}


def test_parse_7():
    cd = ContentDisposition.parse("attachment; filename=foo.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html"}


def test_parse_8():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; filename=foo,bar.html")


def test_parse_9():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; filename=foo.html ;")


def test_parse_10():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; ;filename=foo")


def test_parse_11():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; filename=foo bar.html")


def test_parse_12():
    cd = ContentDisposition.parse("attachment; filename='foo.bar'")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "'foo.bar'"}


def test_parse_13():
    cd = ContentDisposition.parse('attachment; filename="foo-ä.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-ä.html"}


def test_parse_14():
    cd = ContentDisposition.parse('attachment; filename="foo-Ã¤.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-Ã¤.html"}


def test_parse_15():
    cd = ContentDisposition.parse('attachment; filename="foo-%41.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-%41.html"}


def test_parse_16():
    cd = ContentDisposition.parse('attachment; filename="50%.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "50%.html"}


def test_parse_17():
    cd = ContentDisposition.parse('attachment; filename="foo-%\\41.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-%41.html"}


def test_parse_18():
    cd = ContentDisposition.parse('attachment; filename="ä-%41.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "ä-%41.html"}


def test_parse_19():
    cd = ContentDisposition.parse('attachment; filename="foo-%c3%a4-%e2%82%ac.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-%c3%a4-%e2%82%ac.html"}


def test_parse_20():
    cd = ContentDisposition.parse('attachment; filename ="foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html"}


def test_parse_21():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('attachment; filename="foo.html"; filename="bar.html"')


def test_parse_22():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=foo[1](2).html")


def test_parse_23():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=foo-ä.html")


def test_parse_24():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=foo-Ã¤.html")


def test_parse_25():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("filename=foo.html")


def test_parse_26():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("x=y; filename=foo.html")


def test_parse_27():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('"foo; filename=bar;baz"; filename=qux')


def test_parse_28():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("filename=foo.html, filename=bar.html")


def test_parse_29():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("; filename=foo.html")


def test_parse_30():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse(": inline; attachment; filename=foo.html")


def test_parse_31():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("inline; attachment; filename=foo.html")


def test_parse_32():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; inline; filename=foo.html")


def test_parse_33():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('attachment; filename="foo.html".txt')


def test_parse_34():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('attachment; filename="bar')


def test_parse_35():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse('attachment; filename=foo"bar;baz"qux')


def test_parse_36():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse(
            "attachment; filename=foo.html, attachment; filename=bar.html"
        )


def test_parse_37():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; foo=foo filename=bar")


def test_parse_38():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment; filename=bar foo=foo")


def test_parse_39():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("attachment filename=bar")


def test_parse_40():
    with pytest.raises(Exception) as e_info:
        ContentDisposition.parse("filename=foo.html; attachment")


def test_parse_41():
    cd = ContentDisposition.parse("attachment; xfilename=foo.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"xfilename": "foo.html"}


def test_parse_42():
    cd = ContentDisposition.parse('attachment; filename="/foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html"}


def test_parse_43():
    cd = ContentDisposition.parse('attachment; filename="\\\\foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "\\foo.html"}


def test_parse_44():
    cd = ContentDisposition.parse(
        'attachment; creation-date="Wed, 12 Feb 1997 16:29:51 -0500"'
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"creation-date": "Wed, 12 Feb 1997 16:29:51 -0500"}


def test_parse_45():
    cd = ContentDisposition.parse(
        'attachment; modification-date="Wed, 12 Feb 1997 16:29:51 -0500"'
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"modification-date": "Wed, 12 Feb 1997 16:29:51 -0500"}


def test_parse_46():
    cd = ContentDisposition.parse('attachment; example="filename=example.txt"')
    assert cd.type == "attachment"
    assert cd.parameters == {"example": "filename=example.txt"}


def test_parse_47():
    cd = ContentDisposition.parse("attachment; filename*=iso-8859-1''foo-%E4.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-ä.html"}


def test_parse_48():
    cd = ContentDisposition.parse(
        "attachment; filename*=UTF-8''foo-%c3%a4-%e2%82%ac.html"
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-ä-€.html"}


def test_parse_49():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse(
            "attachment; filename*=''foo-%c3%a4-%e2%82%ac.html"
        )


def test_parse_50():
    cd = ContentDisposition.parse("attachment; filename*=UTF-8''foo-a%cc%88.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-ä.html"}


def test_parse_51():
    cd = ContentDisposition.parse(
        "attachment; filename*=iso-8859-1''foo-%c3%a4-%e2%82%ac.html"
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-Ã¤-â?¬.html"}


def test_parse_52():
    cd = ContentDisposition.parse("attachment; filename*=utf-8''foo-%E4.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-\ufffd.html"}


def test_parse_53():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; filename *=UTF-8''foo-%c3%a4.html")


def test_parse_54():
    cd = ContentDisposition.parse("attachment; filename*= UTF-8''foo-%c3%a4.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-ä.html"}


def test_parse_55():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse(
            "attachment; filename*=\"UTF-8''foo-%c3%a4.html\""
        )


def test_parse_56():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse('attachment; filename*="foo%20bar.html"')


def test_parse_57():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; filename*=UTF-8'foo-%c3%a4.html")


def test_parse_58():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; filename*=UTF-8''foo%")


def test_parse_59():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse("attachment; filename*=UTF-8''f%oo.html")


def test_parse_60():
    cd = ContentDisposition.parse("attachment; filename*=UTF-8''A-%2541.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "A-%41.html"}


def test_parse_61():
    cd = ContentDisposition.parse("attachment; filename*=UTF-8''%5cfoo.html")
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "\\foo.html"}


def test_parse_62():
    cd = ContentDisposition.parse('attachment; filename*0="foo."; filename*1="html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*0": "foo.", "filename*1": "html"}


def test_parse_63():
    cd = ContentDisposition.parse(
        'attachment; filename*0="foo"; filename*1="\\b\\a\\r.html"'
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*0": "foo", "filename*1": "bar.html"}


def test_parse_64():
    cd = ContentDisposition.parse(
        "attachment; filename*0*=UTF-8''foo-%c3%a4; filename*1=\".html\""
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*0*": "UTF-8''foo-%c3%a4", "filename*1": ".html"}


def test_parse_65():
    cd = ContentDisposition.parse('attachment; filename*0="foo"; filename*01="bar"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*0": "foo", "filename*01": "bar"}


def test_parse_66():
    cd = ContentDisposition.parse('attachment; filename*0="foo"; filename*2="bar"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*0": "foo", "filename*2": "bar"}


def test_parse_67():
    cd = ContentDisposition.parse('attachment; filename*1="foo."; filename*2="html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*1": "foo.", "filename*2": "html"}


def test_parse_68():
    cd = ContentDisposition.parse('attachment; filename*1="bar"; filename*0="foo"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*1": "bar", "filename*0": "foo"}


def test_parse_69():
    cd = ContentDisposition.parse(
        "attachment; filename=\"foo-ae.html\"; filename*=UTF-8''foo-%c3%a4.html"
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-ä.html"}


def test_parse_70():
    cd = ContentDisposition.parse(
        "attachment; filename*=UTF-8''foo-%c3%a4.html; filename=\"foo-ae.html\""
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo-ä.html"}


def test_parse_71():
    cd = ContentDisposition.parse(
        "attachment; filename*0*=ISO-8859-15''euro-sign%3d%a4; filename*=ISO-8859-1''currency-sign%3d%a4"
    )
    assert cd.type == "attachment"
    assert cd.parameters == {
        "filename": "currency-sign=¤",
        "filename*0*": "ISO-8859-15''euro-sign%3d%a4",
    }


def test_parse_72():
    cd = ContentDisposition.parse('attachment; foobar=x; filename="foo.html"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "foo.html", "foobar": "x"}


def test_parse_73():
    cd = ContentDisposition.parse('attachment; filename*1="bar"; filename*0="foo"')
    assert cd.type == "attachment"
    assert cd.parameters == {"filename*1": "bar", "filename*0": "foo"}


def test_parse_74():
    with pytest.raises(Exception) as e_info:
        cd = ContentDisposition.parse(
            "attachment; filename==?ISO-8859-1?Q?foo-=E4.html?="
        )


def test_parse_75():
    cd = ContentDisposition.parse(
        'attachment; filename="=?ISO-8859-1?Q?foo-=E4.html?="'
    )
    assert cd.type == "attachment"
    assert cd.parameters == {"filename": "=?ISO-8859-1?Q?foo-=E4.html?="}
