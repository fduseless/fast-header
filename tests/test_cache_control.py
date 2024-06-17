from fast_header.cache_control import CacheControl


def test_empty_header():
    cc = CacheControl.parse("")
    assert str(cc) == ""


def test_invalid_header():
    cc = CacheControl.parse("∂")
    assert str(cc) == ""


def test_unknown_properties():
    cc = CacheControl.parse("random-stuff=1244, hello")
    assert str(cc) == ""


def test_duration():
    cc = CacheControl.parse("max-age=4242")
    assert cc.max_age == 4242


def test_immutable():
    cc = CacheControl.parse("immutable=true")
    assert cc.immutable


def test_immutable2():
    cc = CacheControl.parse("immutable")
    assert cc.immutable


def test_max_stale():
    cc = CacheControl.parse("max-stale")
    assert cc.max_stale


def test_max_stale_with_duration():
    cc = CacheControl.parse("max-stale=24")
    assert cc.max_stale == 24


def test_invalid_max_stable():
    cc = CacheControl.parse("max-stale=what")
    assert str(cc) == ""


def test_0_duration():
    cc = CacheControl.parse(
        "max-age=0, s-maxage=0, max-stale=0, min-fresh=0, stale-while-revalidate=0, stale-if-error=0",
    )
    assert cc.max_age == 0
    assert cc.s_maxage == 0
    assert cc.max_stale == 0
    assert cc.min_fresh == 0
    assert cc.stale_while_revalidate == 0
    assert cc.stale_if_error == 0


def test_parse_common_headers():
    cc = CacheControl.parse("no-cache, no-store, must-revalidate")
    assert cc.no_cache
    assert cc.no_store
    assert cc.must_revalidate


def test_parse_common_headers2():
    cc = CacheControl.parse("public, max-age=31536000")
    assert cc.public
    assert cc.max_age == 31_536_000


def test_format_durations():
    cc = CacheControl(
        max_age=4242,
        s_maxage=4343,
        min_fresh=4444,
        stale_while_revalidate=4545,
        stale_if_error=4546,
    )
    assert (
        str(cc)
        == "max-age=4242, min-fresh=4444, s-maxage=4343, stale-while-revalidate=4545, stale-if-error=4546"
    )


def test_format_booleans():
    cc = CacheControl(
        max_stale=True,
        immutable=True,
        must_revalidate=True,
        no_cache=True,
        no_store=True,
        no_transform=True,
        only_if_cached=True,
        private=True,
        proxy_revalidate=True,
        public=True,
    )
    assert (
        str(cc)
        == "max-stale, no-cache, no-store, no-transform, only-if-cached, must-revalidate, proxy-revalidate, private, public, immutable"
    )


def test_zero_duration_values():
    cc = CacheControl(
        max_age=0,
        s_maxage=0,
        public=True,
        max_stale=0,
        min_fresh=0,
        stale_while_revalidate=0,
        stale_if_error=0,
    )
    assert (
        str(cc)
        == "max-age=0, max-stale=0, min-fresh=0, s-maxage=0, public, stale-while-revalidate=0, stale-if-error=0"
    )
