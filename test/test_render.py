import makesite


def test_oneline_template():
    tpl = "foo {{ key1 }} baz {{ key2 }}"
    out = makesite.render(tpl, key1="bar", key2="qux")
    assert out == "foo bar baz qux"


def test_multiline_template():
    tpl = "foo {{ key1 }}\nbaz {{ key1 }}"
    out = makesite.render(tpl, key1="bar")
    assert out, "foo bar\nbaz bar"


def test_repeated_key():
    tpl = "foo {{ key1 }} baz {{ key1 }}"
    out = makesite.render(tpl, key1="bar")
    assert out == "foo bar baz bar"


def test_multiline_placeholder():
    tpl = "foo {{\nkey1\n}} baz {{\nkey2\n}}"
    out = makesite.render(tpl, key1="bar", key2="qux")
    assert out == "foo bar baz qux"
