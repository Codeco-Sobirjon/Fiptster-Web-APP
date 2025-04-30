import hashlib
import hmac
import time


def verify_telegram_auth(data: dict, bot_token: str, allowed_time_skew: int = 86400) -> bool:
    auth_date = int(data.get('auth_date', 0))
    if time.time() - auth_date > allowed_time_skew:
        return False

    check_hash = data.pop('hash')
    sorted_data = sorted(f"{k}={v}" for k, v in data.items())
    data_check_string = '\n'.join(sorted_data)

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

    return hmac_hash == check_hash
