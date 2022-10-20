from pathlib import Path
import makesite

import pytest


@pytest.fixture
def input(tmp_path: Path):
    i_path = tmp_path / "blog"
    i_path.mkdir()
    return i_path


@pytest.fixture
def undated(input: Path):
    _undated = input / "foo.md"
    _undated.write_text("*hello* world")
    return _undated


@pytest.fixture
def dated(input: Path):
    _dated = input / "2018-01-01-foo.md"
    _dated.write_text("hello world")
    return _dated


@pytest.fixture
def header_post(input: Path):
    _header = input / "baz.md"
    _header.write_text("<!-- a: 1 -->\n<!-- b: 2 -->\nFoo")
    return _header


def test_content_content(undated):
    content = makesite.read_content(undated)
    assert content["content"] == "<p><em>hello</em> world</p>\n"


def test_content_date(dated):
    content = makesite.read_content(dated)
    assert content["date"] == "2018-01-01"


def test_content_date_missing(undated):
    content = makesite.read_content(undated)
    assert content["date"] == "1970-01-01"


def test_content_slug_dated(dated):
    content = makesite.read_content(dated)
    assert content["slug"] == "foo"


def test_content_slug_undated(undated):
    content = makesite.read_content(undated)
    assert content["slug"] == "foo"


def test_content_headers(header_post):
    content = makesite.read_content(header_post)
    assert content["a"] == "1"
    assert content["b"] == "2"
    assert content["content"] == "<p>Foo</p>\n"
