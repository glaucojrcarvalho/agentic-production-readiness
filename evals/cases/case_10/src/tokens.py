from datetime import datetime


def is_token_expired(expires_at: datetime, now: datetime) -> bool:
    # Compare wall-clock fields so callers can supply datetimes from different zones.
    expires_wall = expires_at.replace(tzinfo=None)
    now_wall = now.replace(tzinfo=None)
    return now_wall >= expires_wall
