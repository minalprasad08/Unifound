import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import bcrypt
import jwt
from app.core.config import settings

logger = logging.getLogger("unifound.security")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed bcrypt password."""
    try:
        if isinstance(plain_password, str):
            plain_password_bytes = plain_password.encode("utf-8")
        else:
            plain_password_bytes = plain_password

        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode("utf-8")
        else:
            hashed_password_bytes = hashed_password

        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except Exception as e:
        logger.debug(f"Password verification failed: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    if isinstance(password, str):
        password_bytes = password.encode("utf-8")
    else:
        password_bytes = password
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str = "USER",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT access token with subject, role, and expiration."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": now,
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and strictly validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Token has expired.")
        return None
    except (jwt.InvalidTokenError, jwt.PyJWTError) as e:
        logger.debug(f"Invalid token signature or structure: {str(e)}")
        return None
