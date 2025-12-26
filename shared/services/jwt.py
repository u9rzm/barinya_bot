from datetime import datetime, timedelta
from jose import jwt, JWTError

from shared.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None
