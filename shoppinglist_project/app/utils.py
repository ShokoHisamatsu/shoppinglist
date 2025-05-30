# app/utils.py
import secrets

def generate_token(length: int = 20) -> str:
    """URL で安全に使えるトークンを返す（例: 'a1b2c3...'）"""
    return secrets.token_urlsafe(length)
