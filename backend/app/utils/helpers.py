import os
import uuid
import re

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
