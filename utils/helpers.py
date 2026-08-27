import uuid

def generate_id():
    return str(uuid.uuid4())[:8]

def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")
