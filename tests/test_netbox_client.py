"""
Tests for the NetBox API client configuration.
"""

import os
import pytest
import requests
from unittest.mock import MagicMock, patch

from src.config.netbox import get_netbox_client

@pytest.fixture
def mock_env_vars():
    """Set mock environment variables for testing."""
    os.environ['NETBOX_URL'] = 'https://netbox.example.com'
    os.environ['NETBOX_TOKEN'] = 'test_token_123'
    os.environ['NETBOX_SSL_VERIFY'] = 'true'
    
    yield
    
    # Clean up
    os.environ.pop('NETBOX_URL', None)
    os.environ.pop('NETBOX_TOKEN', None)
    os.environ.pop('NETBOX_SSL_VERIFY', None)

@pytest.fixture
def mock_pynetbox():
    """Mock the pynetbox module."""
    with patch('src.config.netbox.pynetbox') as mock_pynetbox:
        mock_api = MagicMock()
        mock_pynetbox.api.return_value = mock_api
        yield mock_pynetbox, mock_api

def test_client_initialization(mock_env_vars, mock_pynetbox):
    """Test that the client is initialized with the correct parameters."""
    mock_pynetbox_module, mock_api = mock_pynetbox
    
    client = get_netbox_client()
    
    # Check that pynetbox.api was called with correct args
    mock_pynetbox_module.api.assert_called_once_with(
        url='https://netbox.example.com', 
        token='test_token_123'
    )
    assert client == mock_api

def test_ssl_verification_true(mock_env_vars, mock_pynetbox):
    """Test that SSL verification is enabled when NETBOX_SSL_VERIFY=true."""
    os.environ['NETBOX_SSL_VERIFY'] = 'true'
    client = get_netbox_client()
    
    # Check that session.verify is True
    assert client.http_session.verify is True

def test_ssl_verification_false(mock_env_vars, mock_pynetbox):
    """Test that SSL verification is disabled when NETBOX_SSL_VERIFY=false."""
    os.environ['NETBOX_SSL_VERIFY'] = 'false'
    client = get_netbox_client()
    
    # Check that session.verify is False
    assert client.http_session.verify is False

def test_read_only_enforcement(mock_env_vars, mock_pynetbox):
    """Test that non-GET requests are blocked by the ReadOnlyAdapter."""
    client = get_netbox_client()
    
    # Create mock request
    request = requests.Request('POST', 'https://netbox.example.com/api/dcim/devices/')
    prepared_request = request.prepare()
    
    # Try to send the request via the adapter
    adapter = client.http_session.get_adapter('https://netbox.example.com')
    
    with pytest.raises(ValueError, match="This is a read-only client"):
        adapter.send(prepared_request)

def test_missing_url_env(mock_env_vars):
    """Test that an error is raised when NETBOX_URL is not set."""
    os.environ.pop('NETBOX_URL')
    
    with pytest.raises(EnvironmentError, match="NETBOX_URL environment variable is not set"):
        get_netbox_client()

def test_missing_token_env(mock_env_vars):
    """Test that an error is raised when NETBOX_TOKEN is not set."""
    os.environ.pop('NETBOX_TOKEN')
    
    with pytest.raises(EnvironmentError, match="NETBOX_TOKEN environment variable is not set"):
        get_netbox_client()