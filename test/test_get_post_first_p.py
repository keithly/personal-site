import makesite


def test_get_post_first_p():
    long_text = "<p>Blah &amp; text didn&#8217;t <em>emphasized</em> more text</p>\n<aside><p>This is an aside.</p></aside>"
    expected_text = "<p>Blah &amp; text didn’t <em>emphasized</em> more text</p>"
    makesite.get_post_first_p(long_text)
    # assert False
    assert makesite.get_post_first_p(long_text) == expected_text
