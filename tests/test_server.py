"""
Basic test script for the NetBox MCP server.

This test validates that the server starts up correctly and
registers the expected tools.
"""

import os
import sys
import subprocess
import json
import pytest
from pathlib import Path

# Make sure we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def mock_env_vars():
    """
    Set mock environment variables for testing
    """
    os.environ['NETBOX_URL'] = 'https://netbox.example.com'
    os.environ['NETBOX_TOKEN'] = 'test_token_123'
    os.environ['NETBOX_SSL_VERIFY'] = 'false'
    
    yield
    
    # Clean up
    os.environ.pop('NETBOX_URL', None)
    os.environ.pop('NETBOX_TOKEN', None)
    os.environ.pop('NETBOX_SSL_VERIFY', None)

def test_server_tools_list(mock_env_vars, monkeypatch):
    """
    Test that the server correctly registers all tools
    """
    # Mock pynetbox API to avoid real network calls
    import pynetbox
    import unittest.mock as mock
    
    # Create a patched version of the pynetbox API
    mock_api = mock.MagicMock()
    monkeypatch.setattr(pynetbox, 'api', lambda **kwargs: mock_api)
    
    # Run mcp tools command to list all tools
    server_path = Path(__file__).parent.parent / "src" / "server.py"
    result = subprocess.run(
        ["python", "-m", "mcptools", "tools", "--format", "json", "python", str(server_path)],
        capture_output=True,
        text=True,
        check=True
    )
    
    # Parse the result
    tools_list = json.loads(result.stdout)
    
    # Verify the tools we expect are registered
    tool_names = [tool["name"] for tool in tools_list["tools"]]
    expected_tools = ["get_devices", "get_device", "ask_about_devices"]
    
    for tool in expected_tools:
        assert tool in tool_names, f"Tool '{tool}' was not found in registered tools"
    
    # Verify schema of tools
    for tool in tools_list["tools"]:
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool
        
        if tool["name"] == "get_devices":
            assert "filter_params" in tool["parameters"]
        elif tool["name"] == "get_device":
            assert "name" in tool["parameters"]
        elif tool["name"] == "ask_about_devices":
            assert "query" in tool["parameters"]