from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def get_password_hash(password: str) -> str:
    """Generate a password hash using bcrypt."""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.check_password_hash(hashed_password, plain_password)
