import os
import hashlib
import hmac
import time
from django.conf import settings


TOKEN = settings.TELEGRAM_BOT_TOKEN


def check_auth(init_data, bot_token):
    hash_received = init_data.get("hash", "")
    if not hash_received:
        return False

    data_check = []
    for key, value in init_data.items():
        if key == "hash":
            continue
        if isinstance(value, list):
            data_check.append((key, value[0]))
        else:
            data_check.append((key, value))

    data_check.sort(key=lambda x: x[0])
    auth_str = "\n".join([f"{k}={v}" for k, v in data_check])

    secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()

    hash_calculated = hmac.new(secret_key, auth_str.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(hash_calculated, hash_received):
        return False

    auth_date = int(init_data.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        return False

    return True
