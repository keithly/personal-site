from pathlib import Path
import makesite
import shutil
import json

import pytest


@pytest.fixture
def setup_content_site_path(tmp_path: Path):
    content_path = tmp_path / "content/blog"
    content_path.mkdir(parents=True)
    shutil.copy(
        "test/2018-01-01-test-post.md", f"{content_path}/2018-01-01-test-post.md"
    )

    output_path = tmp_path / "_site"
    output_path.mkdir()
    return output_path


def test_site_missing(setup_content_site_path: Path, tmp_path: Path):
    """
    test that site is created if missing
    also acts as an integration test
    """

    makesite.main(tmp_path)


def test_site_exists(setup_content_site_path: Path, tmp_path: Path):
    """
    test that the existing site directory is deleted before re-creation
    also acts as an integration test
    """

    file_path = setup_content_site_path / "foo.txt"
    file_path.write_text("foo")

    assert file_path.is_file()
    makesite.main(tmp_path)
    assert file_path.exists() is False


def test_default_params(setup_content_site_path: Path, tmp_path: Path):
    output_path = setup_content_site_path

    makesite.main(tmp_path)

    with open(f"{output_path}/blog/test-post/index.html") as f:
        s1 = f.read()

    with open(f"{output_path}/rss.xml") as f:
        s2 = f.read()

    assert '<a href="/">Keith R. Petersen</a>' in s1
    assert "<title>Test Post &ndash; Keith R. Petersen</title>" in s1
    assert "2018-01-01" in s1

    assert "<link>https://www.keithrpetersen.com/</link>" in s2
    assert "<link>https://www.keithrpetersen.com/blog/test-post/</link>" in s2


def test_json_params(setup_content_site_path: Path, tmp_path: Path):
    output_path = setup_content_site_path
    params_path = tmp_path / "params.json"

    params = {
        "base_path": "/base",
        "subtitle": "Foo",
        "author": "Bar",
        "site_url": "http://localhost/base",
    }
    with open(params_path, "w") as f:
        json.dump(params, f)

    makesite.main(tmp_path)

    with open(f"{output_path}/blog/test-post/index.html") as f:
        s1 = f.read()

    with open(f"{output_path}/rss.xml") as f:
        s2 = f.read()

    assert '<a href="/base/">Keith R. Petersen</a>' in s1
    assert "<title>Test Post &ndash; Keith R. Petersen</title>" in s1
    assert "2018-01-01" in s1

    assert "<link>http://localhost/base/</link>" in s2
    assert "<link>http://localhost/base/blog/test-post/</link>" in s2
