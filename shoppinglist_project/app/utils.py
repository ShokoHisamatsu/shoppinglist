# app/utils.py
import secrets
from .models import SharedList

def generate_token(length: int = 8) -> str:
    """URL で安全に使えるトークンを返す（例: 'a1b2c3...'）"""
    return secrets.token_urlsafe(length)


def generate_unique_token(length: int = 8) -> str:
    """既存と重複しないユニークなトークンを返す"""
    while True:
        token = generate_token(length)
        if not SharedList.objects.filter(url_token=token).exists():
            return token
