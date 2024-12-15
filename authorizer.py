from collections.abc import Callable
from fastapi import FastAPI, HTTPException, Header, Request, Response
import os

from utils import hashString

def is_authenticated(password: str) -> bool:
    admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH')

    input_password_hash = hashString(password)

    return input_password_hash == admin_password_hash

def verify_password(password: str = Header(None)):
    if not password or not is_authenticated(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return password
