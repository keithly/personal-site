from pathlib import Path
import makesite

import pytest


@pytest.fixture
def input(tmp_path: Path):
    i_path = tmp_path / "blog"
    i_path.mkdir()
    return i_path


@pytest.fixture
def output(tmp_path: Path):
    o_path = tmp_path / "site"
    o_path.mkdir()
    return o_path


@pytest.fixture
def undated(input: Path):
    Path(input / "foo.md").write_text("Foo")
    Path(input / "bar.md").write_text("Bar")


@pytest.fixture
def dated(input: Path):
    Path(input / "2018-01-01-foo.md").write_text("Foo")
    Path(input / "2018-01-02-bar.md").write_text("Bar")


@pytest.fixture
def headered(input: Path):
    Path(input / "header-foo.md").write_text("<!-- tag: foo -->Foo")
    Path(input / "header-bar.md").write_text("<!-- title: bar -->Bar")


@pytest.fixture
def placeholder_foo(input: Path):
    Path(input / "placeholder-foo.md").write_text(
        "<!-- title: foo -->{{ title }}:{{ author }}:Foo"
    )


@pytest.fixture
def placeholder_bar(input: Path):
    Path(input / "placeholder-bar.md").write_text(
        "<!-- title: bar --><!-- render: yes -->{{ title }}:{{ author }}:Bar"
    )


def test_pages_undated(undated, input: Path, output: Path):
    src = Path(input / "[fb]*.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ content }}</div>"

    makesite.make_pages(src, dst, tpl)

    assert Path(output / "foo.md").read_text() == "<div><p>Foo</p>\n</div>"
    assert Path(output / "bar.md").read_text() == "<div><p>Bar</p>\n</div>"


def test_pages_dated(dated, input: Path, output: Path):
    src = Path(input / "2*.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ content }}</div>"

    makesite.make_pages(src, dst, tpl)

    assert Path(output / "foo.md").read_text() == "<div><p>Foo</p>\n</div>"
    assert Path(output / "bar.md").read_text() == "<div><p>Bar</p>\n</div>"


def test_pages_layout_params(dated, input: Path, output: Path):
    src = Path(input / "2*.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ slug }}:{{ title }}:{{ date }}:{{ content }}</div>"

    makesite.make_pages(src, dst, tpl, title="Lorem")

    assert (
        Path(output / "foo.md").read_text()
        == "<div>foo:Lorem:2018-01-01:<p>Foo</p>\n</div>"
    )
    assert (
        Path(output / "bar.md").read_text()
        == "<div>bar:Lorem:2018-01-02:<p>Bar</p>\n</div>"
    )


def test_pages_return_value(dated, input: Path, output: Path):
    src = Path(input / "2*.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ content }}</div>"

    posts = makesite.make_pages(src, dst, tpl)

    assert len(posts) == 2
    assert posts[0]["date"] == "2018-01-02"
    assert posts[1]["date"] == "2018-01-01"


def test_content_header_params(headered, input: Path, output: Path):
    """Test that header params from one post are not used in another post."""

    src = Path(input / "header*.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "{{ title }}:{{ tag }}:{{ content }}"

    makesite.make_pages(src, dst, tpl)

    assert Path(output / "header-foo.md").read_text() == "{{ title }}:foo:<p>Foo</p>\n"
    assert Path(output / "header-bar.md").read_text() == "bar:{{ tag }}:<p>Bar</p>\n"


def test_content_no_rendering(placeholder_foo, input: Path, output: Path):
    """Test that placeholders are not populated in content rendering by default."""

    src = Path(input / "placeholder-foo.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ content }}</div>"

    makesite.make_pages(src, dst, tpl, author="Admin")

    assert (
        Path(output / "placeholder-foo.md").read_text()
        == "<div><p>{{ title }}:{{ author }}:Foo</p>\n</div>"
    )


def test_content_rendering_via_kwargs(placeholder_foo, input: Path, output: Path):
    """Test that placeholders are populated in content rendering when requested in make_pages."""

    src = Path(input / "placeholder-foo.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ content }}</div>"

    makesite.make_pages(src, dst, tpl, author="Admin", render="yes")

    assert (
        Path(output / "placeholder-foo.md").read_text()
        == "<div><p>foo:Admin:Foo</p>\n</div>"
    )


def test_content_rendering_via_header(placeholder_bar, input: Path, output: Path):
    """Test that placeholders are populated in content rendering when requested in content header."""

    src = Path(input / "placeholder-bar.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ content }}</div>"

    makesite.make_pages(src, dst, tpl, author="Admin")

    assert (
        Path(output / "placeholder-bar.md").read_text()
        == "<div><p>bar:Admin:Bar</p>\n</div>"
    )


@pytest.mark.skip()
def test_rendered_content_in_summary(
    placeholder_foo, placeholder_bar, input: Path, output: Path
):
    """Test that placeholders are populated in summary if and only if content rendering is enabled."""

    src = Path(input / "placeholder*.md").as_posix()
    post_dst = Path(output / "{{ slug }}.md").as_posix()
    list_dst = Path(output / "list.md").as_posix()
    post_layout = ""
    list_layout = "<div>{{ content }}</div>"
    item_layout = "{{ summary }}"

    posts = makesite.make_pages(src, post_dst, post_layout, author="Admin")
    makesite.make_list(posts, list_dst, list_layout, item_layout)

    assert (
        Path(output, "list.md").read_text()
        == "<div><p>{{ title }}:{{ author }}:Foo</p><p>bar:Admin:Bar</p></div>"
    )


def test_pages_canonical_slug_params(dated, input: Path, output: Path):
    src = Path(input / "2*.md").as_posix()
    dst = Path(output / "{{ slug }}.md").as_posix()
    tpl = "<div>{{ slug }}:{{ canonical_url }}:{{ date }}:{{ content }}</div>"
    params = {"site_url": "https://www.example.com"}

    makesite.make_pages(
        src, dst, tpl, **params, canonical_url=params["site_url"] + "/{{ slug }}/"
    )

    assert (
        Path(output / "foo.md").read_text()
        == "<div>foo:https://www.example.com/foo/:2018-01-01:<p>Foo</p>\n</div>"
    )
    assert (
        Path(output / "bar.md").read_text()
        == "<div>bar:https://www.example.com/bar/:2018-01-02:<p>Bar</p>\n</div>"
    )
