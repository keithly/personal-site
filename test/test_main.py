from pathlib import Path
import makesite
import shutil
import json

import pytest

from test import path


@pytest.fixture
def set_site_path(tmp_path: Path):
    site_dir = "_blah"
    output_path = tmp_path / site_dir
    output_path.mkdir()
    return output_path


@pytest.fixture
def setup_teardown():
    path.move("params.json", "params.json.backup")
    path.move("test/2018-01-01-test-post.md", "content/blog/2018-01-01-test-post.md")
    yield
    path.move("params.json.backup", "params.json")
    path.move("content/blog/2018-01-01-test-post.md", "test/2018-01-01-test-post.md")


def test_site_missing(setup_teardown, set_site_path):
    """
    test that site is created if missing
    also acts as an integration test
    """

    makesite.main(set_site_path)


def test_site_exists(setup_teardown, set_site_path):
    """
    test that the existing site directory is deleted before re-creation
    also acts as an integration test
    """

    output_path = set_site_path
    file_path = output_path / "foo.txt"
    with open(file_path, "w") as f:
        f.write("foo")

    assert file_path.is_file()
    makesite.main(output_path)
    assert file_path.exists() is False


def test_default_params(setup_teardown, set_site_path):
    output_path = set_site_path

    makesite.main(output_path)

    with open(f"{output_path}/blog/test-post/index.html") as f:
        s1 = f.read()

    with open(f"{output_path}/rss.xml") as f:
        s2 = f.read()

    shutil.rmtree(output_path)

    assert '<a href="/">Keith R. Petersen</a>' in s1
    assert "<title>Test Post</title>" in s1
    assert "2018-01-01" in s1

    assert "<link>http://localhost:8000/</link>" in s2
    assert "<link>http://localhost:8000/blog/test-post/</link>" in s2


def test_json_params(setup_teardown, set_site_path):
    output_path = set_site_path

    params_path = Path("params.json")
    params = {
        "base_path": "/base",
        "subtitle": "Foo",
        "author": "Bar",
        "site_url": "http://localhost/base",
    }
    with open(params_path, "w") as f:
        json.dump(params, f)

    makesite.main(output_path, params_path)

    with open(f"{output_path}/blog/test-post/index.html") as f:
        s1 = f.read()

    with open(f"{output_path}/rss.xml") as f:
        s2 = f.read()

    shutil.rmtree(output_path)

    assert '<a href="/base/">Keith R. Petersen</a>' in s1
    assert "<title>Test Post</title>" in s1
    assert "2018-01-01" in s1

    assert "<link>http://localhost/base/</link>" in s2
    assert "<link>http://localhost/base/blog/test-post/</link>" in s2
