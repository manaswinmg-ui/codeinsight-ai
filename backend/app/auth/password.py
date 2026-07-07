"""Password hashing and verification using bcrypt directly."""

import bcrypt


class PasswordService:
    """Production-grade password hashing using bcrypt directly."""

    def hash_password(self, plain_password: str) -> str:
        """Hash a plain-text password with bcrypt (auto-salted)."""
        password_bytes = plain_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a bcrypt hash."""
        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False


password_service = PasswordService()
