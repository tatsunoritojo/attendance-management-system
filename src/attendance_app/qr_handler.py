import requests
from pathlib import Path


def download_qr(url: str, dest: Path) -> Path:
    """Download QR code image from URL to dest path."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest