"""
Authentication module for sample project
"""
import hashlib
import secrets
from typing import Optional, Dict


class User:
    """User model"""
    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = True
        self.login_attempts = 0


class AuthenticationService:
    """Handles user authentication"""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, str] = {}
        self.max_login_attempts = 3

    def register_user(self, username: str, email: str, password: str) -> bool:
        """Register a new user"""
        if username in self.users:
            return False

        if not self._validate_email(email):
            return False

        if not self._validate_password(password):
            return False

        password_hash = self._hash_password(password)
        self.users[username] = User(username, email, password_hash)
        return True

    def login(self, username: str, password: str) -> Optional[str]:
        """Login user and return session token"""
        if username not in self.users:
            return None

        user = self.users[username]

        if not user.is_active:
            return None

        if user.login_attempts >= self.max_login_attempts:
            user.is_active = False
            return None

        password_hash = self._hash_password(password)
        if password_hash != user.password_hash:
            user.login_attempts += 1
            # Lock account if max attempts reached
            if user.login_attempts >= self.max_login_attempts:
                user.is_active = False
            return None

        # Reset login attempts on successful login
        user.login_attempts = 0

        # Generate session token
        token = secrets.token_hex(32)
        self.sessions[token] = username
        return token

    def logout(self, token: str) -> bool:
        """Logout user"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False

    def validate_session(self, token: str) -> Optional[str]:
        """Validate session token and return username"""
        return self.sessions.get(token)

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        return '@' in email and '.' in email.split('@')[1]

    def _validate_password(self, password: str) -> bool:
        """Validate password strength"""
        return len(password) >= 8

    def reset_password(self, username: str, new_password: str) -> bool:
        """Reset user password"""
        if username not in self.users:
            return False

        if not self._validate_password(new_password):
            return False

        user = self.users[username]
        user.password_hash = self._hash_password(new_password)
        user.login_attempts = 0
        user.is_active = True
        return True
