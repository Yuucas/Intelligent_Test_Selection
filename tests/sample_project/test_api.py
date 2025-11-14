"""
Tests for API module
"""
import pytest
from .api import APIClient, Response, RateLimiter, APIError


class TestAPIClient:
    """Test cases for APIClient"""

    @pytest.fixture
    def client(self):
        """Create API client fixture"""
        return APIClient('https://api.example.com', timeout=30)

    def test_client_initialization(self, client):
        """Test API client initialization"""
        assert client.base_url == 'https://api.example.com'
        assert client.timeout == 30
        assert 'Content-Type' in client.headers

    def test_set_auth_token(self, client):
        """Test setting auth token"""
        client.set_auth_token('test_token_123')
        assert client.auth_token == 'test_token_123'
        assert 'Authorization' in client.headers
        assert client.headers['Authorization'] == 'Bearer test_token_123'

    def test_clear_auth_token(self, client):
        """Test clearing auth token"""
        client.set_auth_token('test_token_123')
        client.clear_auth_token()
        assert client.auth_token is None
        assert 'Authorization' not in client.headers

    def test_get_request(self, client):
        """Test GET request"""
        response = client.get('/users')
        assert response.status_code == 200
        assert response.data['method'] == 'GET'

    def test_get_request_with_params(self, client):
        """Test GET request with parameters"""
        response = client.get('/users', params={'page': 1, 'limit': 10})
        assert response.status_code == 200
        assert 'page=1' in response.data['url']
        assert 'limit=10' in response.data['url']

    def test_post_request(self, client):
        """Test POST request"""
        data = {'name': 'John', 'email': 'john@example.com'}
        response = client.post('/users', data=data)
        assert response.status_code == 201
        assert response.data['method'] == 'POST'
        assert response.data['data'] == data

    def test_post_request_no_data(self, client):
        """Test POST request without data"""
        response = client.post('/users')
        assert response.status_code == 400

    def test_put_request(self, client):
        """Test PUT request"""
        data = {'name': 'John Updated'}
        response = client.put('/users/1', data=data)
        assert response.status_code == 200
        assert response.data['method'] == 'PUT'

    def test_put_request_no_data(self, client):
        """Test PUT request without data"""
        response = client.put('/users/1')
        assert response.status_code == 400

    def test_delete_request(self, client):
        """Test DELETE request"""
        response = client.delete('/users/1')
        assert response.status_code == 204
        assert response.data['method'] == 'DELETE'

    def test_patch_request(self, client):
        """Test PATCH request"""
        data = {'email': 'newemail@example.com'}
        response = client.patch('/users/1', data=data)
        assert response.status_code == 200
        assert response.data['method'] == 'PATCH'

    def test_patch_request_no_data(self, client):
        """Test PATCH request without data"""
        response = client.patch('/users/1')
        assert response.status_code == 400


class TestResponse:
    """Test cases for Response"""

    def test_response_initialization(self):
        """Test response initialization"""
        response = Response(200, {'message': 'Success'})
        assert response.status_code == 200
        assert response.data == {'message': 'Success'}

    def test_response_with_headers(self):
        """Test response with headers"""
        headers = {'X-Custom-Header': 'value'}
        response = Response(200, {'message': 'Success'}, headers=headers)
        assert response.headers == headers

    def test_response_json(self):
        """Test response JSON conversion"""
        response = Response(200, {'message': 'Success'})
        json_data = response.json()
        assert json_data['status_code'] == 200
        assert json_data['data'] == {'message': 'Success'}


class TestRateLimiter:
    """Test cases for RateLimiter"""

    @pytest.fixture
    def limiter(self):
        """Create rate limiter fixture"""
        return RateLimiter(max_requests=5, window_seconds=60)

    def test_limiter_initialization(self, limiter):
        """Test rate limiter initialization"""
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 60
        assert len(limiter.requests) == 0

    def test_can_make_request_under_limit(self, limiter):
        """Test can make request when under limit"""
        assert limiter.can_make_request() is True

    def test_record_request(self, limiter):
        """Test recording request"""
        limiter.record_request()
        assert len(limiter.requests) == 1

    def test_can_make_request_at_limit(self, limiter):
        """Test can make request at limit"""
        for _ in range(5):
            limiter.record_request()
        assert limiter.can_make_request() is False

    def test_wait_time(self, limiter):
        """Test wait time calculation"""
        wait = limiter.wait_time()
        assert wait == 0.0

        # Fill up the limiter
        for _ in range(5):
            limiter.record_request()

        wait = limiter.wait_time()
        assert wait > 0


class TestAPIError:
    """Test cases for APIError"""

    def test_api_error_initialization(self):
        """Test API error initialization"""
        error = APIError('Not Found', 404)
        assert error.message == 'Not Found'
        assert error.status_code == 404
        assert 'API Error 404' in str(error)
