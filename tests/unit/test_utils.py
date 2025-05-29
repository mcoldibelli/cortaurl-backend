import string
from layers.shared.python.utils import generate_code, is_valid_domain

def test_valid_domain():
    assert is_valid_domain("https://google.com")
    assert is_valid_domain("http://test.com")
    assert not is_valid_domain("ftp://test.com")
    assert not is_valid_domain("just-text")

def test_generate_code_default_length():
    code = generate_code()
    assert isinstance(code, str)
    assert len(code) == 6
    allowed_chars = string.ascii_letters + string.digits
    assert all(char in allowed_chars for char in code)

def test_generate_code_custom_length():
    for length in [1, 8, 12]:
        code = generate_code(length)
        assert len(code) == length

def test_generate_code_uniqueness():
    code = {generate_code() for _ in range(1000)}
    assert len(code) > 990