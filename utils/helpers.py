import uuid
import re

def generate_id():
    return str(uuid.uuid4())[:8]

def is_valid_url(url):
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None
