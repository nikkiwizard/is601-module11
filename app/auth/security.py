from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    if raw_password is None:
        raise ValueError("Password cannot be None")

    # Only apply bcrypt-specific truncation when a bcrypt scheme is configured
    schemes = [s.lower() for s in pwd_context.schemes()]
    if any("bcrypt" in s for s in schemes):
        raw_bytes = raw_password.encode("utf-8")
        if len(raw_bytes) > 72:
            raw_password = raw_bytes[:72].decode("utf-8", errors="ignore")

    return pwd_context.hash(raw_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)