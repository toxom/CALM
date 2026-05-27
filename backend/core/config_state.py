# backend/core/config_state.py
from backend.api.config.routes import _current_config

def get_config():
    return _current_config