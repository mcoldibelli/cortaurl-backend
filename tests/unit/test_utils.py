from layers.shared.python.utils import is_valid_url

def test_valid_url():
    assert is_valid_url("https://google.com")
    assert is_valid_url("http://test.com")
    assert not is_valid_url("ftp://test.com")
    assert not is_valid_url("just-text")