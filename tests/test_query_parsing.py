"""
Tests for natural language query parsing functionality.
"""

import pytest
import sys
from pathlib import Path

# Make sure we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.devices import _parse_natural_language_query

def test_site_extraction():
    """Test that site information is correctly extracted from queries."""
    # Test different site extraction patterns
    params1 = _parse_natural_language_query("Show me all devices at site SF1")
    assert params1.site == "SF1"
    
    params2 = _parse_natural_language_query("List devices in NYC location")
    assert params2.site == "NYC"
    
    params3 = _parse_natural_language_query("Get devices from LAB3 site")
    assert params3.site == "LAB3"
    
    params4 = _parse_natural_language_query("Find all devices for site DC2")
    assert params4.site == "DC2"

def test_role_extraction():
    """Test that device role information is correctly extracted."""
    params1 = _parse_natural_language_query("List all firewall devices")
    assert params1.role == "firewall"
    
    params2 = _parse_natural_language_query("Show me the router at site NYC")
    assert params2.role == "router"
    assert params2.site == "NYC"
    
    params3 = _parse_natural_language_query("Get all switch devices")
    assert params3.role == "switch"
    
    params4 = _parse_natural_language_query("Find server devices")
    assert params4.role == "server"

def test_status_extraction():
    """Test that status information is correctly extracted."""
    params1 = _parse_natural_language_query("Show all active devices")
    assert params1.status == "active"
    
    params2 = _parse_natural_language_query("List planned devices")
    assert params2.status == "planned"
    
    params3 = _parse_natural_language_query("Get failed devices at site LAB1")
    assert params3.status == "failed"
    assert params3.site == "LAB1"

def test_device_name_extraction():
    """Test that device name is correctly extracted."""
    params1 = _parse_natural_language_query("Tell me about device core-sw01")
    assert params1.name == "core-sw01"
    
    params2 = _parse_natural_language_query("Get information for device sf1.fw1")
    assert params2.name == "sf1.fw1"

def test_limit_extraction():
    """Test that limit is correctly extracted."""
    params1 = _parse_natural_language_query("Show me the first 5 devices")
    assert params1.limit == 5
    
    params2 = _parse_natural_language_query("List top 10 switches")
    assert params2.limit == 10
    assert params2.role == "switch"
    
    # Test limit bounds
    params3 = _parse_natural_language_query("Show limit 2000 devices")
    assert params3.limit == 1000  # Should cap at 1000

def test_complex_queries():
    """Test extraction from complex queries with multiple parameters."""
    params1 = _parse_natural_language_query("Show me all active firewalls at site DC1")
    assert params1.status == "active"
    assert params1.role == "firewall"
    assert params1.site == "DC1"
    
    params2 = _parse_natural_language_query("List the first 10 offline switches in LAB2")
    assert params2.limit == 10
    assert params2.status == "offline"
    assert params2.role == "switch"
    assert params2.site == "LAB2"