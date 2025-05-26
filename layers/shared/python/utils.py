import string, random, re

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_valid_url(url):
    pattern = re.compile(
        r'^(https?://)?([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,})(:\d+)?(/[^\s]*)?$'
    )
    return bool(pattern.match(url))
