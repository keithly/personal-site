from pathlib import Path


import makesite


def test_fwrite(tmp_path: Path):
    text = "baz\nqux\n"
    filepath = tmp_path / "foo.txt"

    makesite.fwrite(filepath, text)

    text_read = filepath.read_text()
    assert text_read == text


def test_fwrite_makedir(tmp_path: Path):
    text = "baz\nqux\n"
    dirpath = tmp_path / "foo" / "bar"
    filepath = dirpath / "foo.txt"

    makesite.fwrite(filepath, text)

    text_read = filepath.read_text()
    assert dirpath.is_dir()
    assert text_read == text
