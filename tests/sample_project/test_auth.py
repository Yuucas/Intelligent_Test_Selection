"""
Tests for authentication module
"""
import pytest
from .auth import AuthenticationService, User


class TestAuthenticationService:
    """Test cases for AuthenticationService"""

    @pytest.fixture
    def auth_service(self):
        """Create auth service fixture"""
        return AuthenticationService()

    def test_register_user_success(self, auth_service):
        """Test successful user registration"""
        result = auth_service.register_user('john', 'john@example.com', 'password123')
        assert result is True
        assert 'john' in auth_service.users

    def test_register_user_duplicate_username(self, auth_service):
        """Test registration with duplicate username"""
        auth_service.register_user('john', 'john@example.com', 'password123')
        result = auth_service.register_user('john', 'john2@example.com', 'password456')
        assert result is False

    def test_register_user_invalid_email(self, auth_service):
        """Test registration with invalid email"""
        result = auth_service.register_user('john', 'invalid-email', 'password123')
        assert result is False

    def test_register_user_weak_password(self, auth_service):
        """Test registration with weak password"""
        result = auth_service.register_user('john', 'john@example.com', 'weak')
        assert result is False

    def test_login_success(self, auth_service):
        """Test successful login"""
        auth_service.register_user('john', 'john@example.com', 'password123')
        token = auth_service.login('john', 'password123')
        assert token is not None
        assert len(token) == 64  # hex token length

    def test_login_invalid_username(self, auth_service):
        """Test login with invalid username"""
        token = auth_service.login('nonexistent', 'password123')
        assert token is None

    def test_login_wrong_password(self, auth_service):
        """Test login with wrong password"""
        auth_service.register_user('john', 'john@example.com', 'password123')
        token = auth_service.login('john', 'wrongpassword')
        assert token is None

    def test_login_attempts_lockout(self, auth_service):
        """Test account lockout after max login attempts"""
        auth_service.register_user('john', 'john@example.com', 'password123')

        # Try wrong password multiple times
        for _ in range(3):
            auth_service.login('john', 'wrongpassword')

        # Account should be locked
        user = auth_service.users['john']
        assert user.is_active is False

        # Even correct password should fail
        token = auth_service.login('john', 'password123')
        assert token is None

    def test_logout_success(self, auth_service):
        """Test successful logout"""
        auth_service.register_user('john', 'john@example.com', 'password123')
        token = auth_service.login('john', 'password123')
        result = auth_service.logout(token)
        assert result is True
        assert token not in auth_service.sessions

    def test_logout_invalid_token(self, auth_service):
        """Test logout with invalid token"""
        result = auth_service.logout('invalid_token')
        assert result is False

    def test_validate_session_valid(self, auth_service):
        """Test session validation with valid token"""
        auth_service.register_user('john', 'john@example.com', 'password123')
        token = auth_service.login('john', 'password123')
        username = auth_service.validate_session(token)
        assert username == 'john'

    def test_validate_session_invalid(self, auth_service):
        """Test session validation with invalid token"""
        username = auth_service.validate_session('invalid_token')
        assert username is None

    def test_reset_password_success(self, auth_service):
        """Test successful password reset"""
        auth_service.register_user('john', 'john@example.com', 'password123')
        result = auth_service.reset_password('john', 'newpassword123')
        assert result is True

        # Should be able to login with new password
        token = auth_service.login('john', 'newpassword123')
        assert token is not None

    def test_reset_password_invalid_user(self, auth_service):
        """Test password reset for non-existent user"""
        result = auth_service.reset_password('nonexistent', 'newpassword123')
        assert result is False

    def test_reset_password_weak(self, auth_service):
        """Test password reset with weak password"""
        auth_service.register_user('john', 'john@example.com', 'password123')
        result = auth_service.reset_password('john', 'weak')
        assert result is False

    def test_reset_password_unlocks_account(self, auth_service):
        """Test that password reset unlocks locked account"""
        auth_service.register_user('john', 'john@example.com', 'password123')

        # Lock account
        for _ in range(3):
            auth_service.login('john', 'wrongpassword')

        # Reset password should unlock
        auth_service.reset_password('john', 'newpassword123')
        user = auth_service.users['john']
        assert user.is_active is True
        assert user.login_attempts == 0


class TestUser:
    """Test cases for User class"""

    def test_user_initialization(self):
        """Test user object initialization"""
        user = User('john', 'john@example.com', 'hash123')
        assert user.username == 'john'
        assert user.email == 'john@example.com'
        assert user.password_hash == 'hash123'
        assert user.is_active is True
        assert user.login_attempts == 0
