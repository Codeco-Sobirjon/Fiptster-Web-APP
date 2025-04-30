import os
import hashlib
import hmac
import time
from django.conf import settings


TOKEN = settings.TELEGRAM_BOT_TOKEN
# LOCAL_TELEGRAM, PUBLICK_TELEGRAM

def check_auth(init_data, bot_token):
    """
    Improved Telegram WebApp initData authentication
    """
    # Extract the hash
    hash_received = init_data.get("hash", "")
    if not hash_received:
        return False

    # Prepare data items for authentication string
    data_check = []
    for key, value in init_data.items():
        if key == "hash":
            continue
        # Handle both string and list values (from parse_qs)
        if isinstance(value, list):
            data_check.append((key, value[0]))
        else:
            data_check.append((key, value))

    # Sort by key and create auth string
    data_check.sort(key=lambda x: x[0])
    auth_str = "\n".join([f"{k}={v}" for k, v in data_check])

    # Calculate secret key
    secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()

    # Calculate hash
    hash_calculated = hmac.new(secret_key, auth_str.encode(), hashlib.sha256).hexdigest()

    # Compare hashes
    if not hmac.compare_digest(hash_calculated, hash_received):
        return False

    # Check auth date (within 1 day)
    auth_date = int(init_data.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        return False

    return True
