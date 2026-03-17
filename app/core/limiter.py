from slowapi import Limiter
from slowapi.util import get_remote_address
import os

limiter = Limiter(
    key_func=get_remote_address, # Identifies user IP
    headers_enabled=True,
    enabled=os.getenv("ENV") != 'testing')  # Rate limited disabled for pytest

# For PRO version limiter will have added ID verification