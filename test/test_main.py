import makesite
import os
import shutil
import json

import pytest

from test import path


@pytest.fixture
def setup_teardown():
    path.move("_site", "_site.backup")
    path.move("params.json", "params.json.backup")
    path.move("test/2018-01-01-test-post.md", "content/blog/2018-01-01-test-post.md")
    yield
    path.move("_site.backup", "_site")
    path.move("params.json.backup", "params.json")
    path.move("content/blog/2018-01-01-test-post.md", "test/2018-01-01-test-post.md")


def test_site_missing(setup_teardown):
    makesite.main()


def test_site_exists(setup_teardown):
    os.mkdir("_site")
    with open("_site/foo.txt", "w") as f:
        f.write("foo")

    assert os.path.isfile("_site/foo.txt")
    makesite.main()
    assert os.path.isfile("_site/foo.txt") is False


def test_default_params(setup_teardown):
    makesite.main()

    with open("_site/blog/test-post/index.html") as f:
        s1 = f.read()

    with open("_site/rss.xml") as f:
        s2 = f.read()

    shutil.rmtree("_site")

    assert '<a href="/">Keith R. Petersen</a>' in s1
    assert "<title>Test Post</title>" in s1
    assert "2018-01-01" in s1

    assert "<link>http://localhost:8000/</link>" in s2
    assert "<link>http://localhost:8000/blog/test-post/</link>" in s2


def test_json_params(setup_teardown):
    params = {
        "base_path": "/base",
        "subtitle": "Foo",
        "author": "Bar",
        "site_url": "http://localhost/base",
    }
    with open("params.json", "w") as f:
        json.dump(params, f)

    makesite.main()

    with open("_site/blog/test-post/index.html") as f:
        s1 = f.read()

    with open("_site/rss.xml") as f:
        s2 = f.read()

    shutil.rmtree("_site")

    assert '<a href="/base/">Keith R. Petersen</a>' in s1
    assert "<title>Test Post</title>" in s1
    assert "2018-01-01" in s1

    assert "<link>http://localhost/base/</link>" in s2
    assert "<link>http://localhost/base/blog/test-post/</link>" in s2
