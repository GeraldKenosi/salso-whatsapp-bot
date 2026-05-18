import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_users():
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_users(users):
    _ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def get_or_create_user(wa_id, profile_name=None):
    """Get existing user or create a new one. Returns (user, is_new)."""
    users = _load_users()
    if wa_id in users:
        user = users[wa_id]
        user["last_seen"] = datetime.utcnow().isoformat()
        user["profile_name"] = profile_name or user.get("profile_name", "Unknown")
        _save_users(users)
        return user, False

    user = {
        "wa_id": wa_id,
        "profile_name": profile_name or "Unknown",
        "first_seen": datetime.utcnow().isoformat(),
        "last_seen": datetime.utcnow().isoformat(),
        "registered": False,
        "name": None,
        "email": None,
        "phone": None,
        "organisation": None,
        "role": None,
    }
    users[wa_id] = user
    _save_users(users)
    return user, True


def update_user(wa_id, **kwargs):
    users = _load_users()
    if wa_id not in users:
        return None
    for k, v in kwargs.items():
        if v is not None:
            users[wa_id][k] = v
    users[wa_id]["last_seen"] = datetime.utcnow().isoformat()
    _save_users(users)
    return users[wa_id]


def is_registered(wa_id):
    users = _load_users()
    user = users.get(wa_id)
    if not user:
        return False
    return user.get("registered", False) and bool(user.get("name")) and bool(user.get("email"))
