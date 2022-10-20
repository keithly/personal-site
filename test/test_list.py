from pathlib import Path
import makesite

import pytest


@pytest.fixture
def output(tmp_path: Path):
    o_path = tmp_path / "site"
    o_path.mkdir()
    return o_path


def test_list(output: Path):
    posts = [{"content": "Foo"}, {"content": "Bar"}]
    dst = Path(output / "list.html")
    list_layout = "<div>{{ content }}</div>"
    item_layout = "<p>{{ content }}</p>"

    makesite.make_list(posts, dst.as_posix(), list_layout, item_layout)

    assert dst.read_text() == "<div><p>Foo</p><p>Bar</p></div>"


def test_list_params(output: Path):
    posts = [{"content": "Foo", "title": "foo"}, {"content": "Bar", "title": "bar"}]
    dst = Path(output / "list.html")
    list_layout = "<div>{{ key }}:{{ title }}:{{ content }}</div>"
    item_layout = "<p>{{ key }}:{{ title }}:{{ content }}</p>"

    makesite.make_list(
        posts, dst.as_posix(), list_layout, item_layout, key="val", title="lorem"
    )

    text = dst.read_text()
    assert text == "<div>val:lorem:<p>val:foo:Foo</p><p>val:bar:Bar</p></div>"


def test_dst_params(output: Path):
    posts = [{"content": "Foo"}, {"content": "Bar"}]
    dst = Path(output / "{{ key }}.html").as_posix()
    list_layout = "<div>{{ content }}</div>"
    item_layout = "<p>{{ content }}</p>"

    makesite.make_list(posts, dst, list_layout, item_layout, key="val")

    expected_path = Path(output / "val.html")
    assert expected_path.is_file()
    assert expected_path.read_text() == "<div><p>Foo</p><p>Bar</p></div>"
