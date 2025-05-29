import string, random, re
from urllib.parse import urlparse

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_valid_domain(url):
    # Checa se o domínio é válido, pelo menos contém um ponto e nome
    parsed = urlparse(normalize_url(url))
    domain = parsed.netloc
    return '.' in domain and not domain.startswith('.')

def normalize_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    return url