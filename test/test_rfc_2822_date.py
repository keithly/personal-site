import makesite


def test_epoch():
    assert makesite.rfc_2822_format("1970-01-01") == "Thu, 01 Jan 1970 00:00:00 +0000"


def test_2018_06_16():
    assert makesite.rfc_2822_format("2018-06-16") == "Sat, 16 Jun 2018 00:00:00 +0000"
