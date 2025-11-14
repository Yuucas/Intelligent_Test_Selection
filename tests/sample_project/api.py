"""
API module for sample project
"""
from typing import Dict, Any, Optional, List
import json


class Response:
    """HTTP Response object"""
    def __init__(self, status_code: int, data: Any, headers: Optional[Dict] = None):
        self.status_code = status_code
        self.data = data
        self.headers = headers or {}

    def json(self) -> Dict:
        """Get response as JSON"""
        return {
            'status_code': self.status_code,
            'data': self.data,
            'headers': self.headers
        }


class APIClient:
    """REST API Client"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TestClient/1.0'
        }
        self.auth_token: Optional[str] = None

    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.auth_token = token
        self.headers['Authorization'] = f'Bearer {token}'

    def clear_auth_token(self):
        """Clear authentication token"""
        self.auth_token = None
        if 'Authorization' in self.headers:
            del self.headers['Authorization']

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Response:
        """Make GET request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Simulate API call
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"

        # Mock response
        return Response(200, {'url': url, 'method': 'GET'})

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Response:
        """Make POST request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if data is None:
            return Response(400, {'error': 'No data provided'})

        # Mock response
        return Response(201, {'url': url, 'method': 'POST', 'data': data})

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Response:
        """Make PUT request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if data is None:
            return Response(400, {'error': 'No data provided'})

        # Mock response
        return Response(200, {'url': url, 'method': 'PUT', 'data': data})

    def delete(self, endpoint: str) -> Response:
        """Make DELETE request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Mock response
        return Response(204, {'url': url, 'method': 'DELETE'})

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Response:
        """Make PATCH request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if data is None:
            return Response(400, {'error': 'No data provided'})

        # Mock response
        return Response(200, {'url': url, 'method': 'PATCH', 'data': data})


class APIError(Exception):
    """API Error exception"""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(f"API Error {status_code}: {message}")


class RateLimiter:
    """Rate limiter for API requests"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []

    def can_make_request(self) -> bool:
        """Check if request can be made"""
        import time
        current_time = time.time()

        # Remove old requests
        self.requests = [
            req_time for req_time in self.requests
            if current_time - req_time < self.window_seconds
        ]

        return len(self.requests) < self.max_requests

    def record_request(self):
        """Record a new request"""
        import time
        self.requests.append(time.time())

    def wait_time(self) -> float:
        """Get time to wait before next request"""
        import time
        if self.can_make_request():
            return 0.0

        current_time = time.time()
        oldest_request = min(self.requests)
        return self.window_seconds - (current_time - oldest_request)
