"""
Common test configuration and fixtures.
"""

import os
import pytest
import logging
import sys
from pathlib import Path

# Make sure we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Suppress noisy loggers
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

@pytest.fixture
def sample_device_data():
    """Provide sample device data for testing."""
    return {
        'id': 123,
        'name': 'test-device-01',
        'device_type': {
            'id': 1,
            'model': 'Cisco Catalyst 3850'
        },
        'device_role': {
            'id': 1,
            'name': 'access-switch'
        },
        'site': {
            'id': 1,
            'name': 'NYC'
        },
        'status': {
            'value': 'active',
            'label': 'Active'
        },
        'primary_ip4': {
            'id': 1,
            'address': '192.168.1.1/24'
        },
        'serial': 'ABC123XYZ',
        'description': 'Test device',
        'tags': [
            {
                'id': 1,
                'name': 'production'
            },
            {
                'id': 2,
                'name': 'managed'
            }
        ]
    }

@pytest.fixture
def sample_device_list():
    """Provide a sample list of devices for testing."""
    return [
        {
            'id': 1,
            'name': 'nyc-sw01',
            'device_type': {'model': 'Cisco Catalyst 3850'},
            'device_role': {'name': 'access-switch'},
            'site': {'name': 'NYC'},
            'status': {'value': 'active'},
            'serial': 'ABC123'
        },
        {
            'id': 2,
            'name': 'nyc-rtr01',
            'device_type': {'model': 'Cisco ASR 1000'},
            'device_role': {'name': 'router'},
            'site': {'name': 'NYC'},
            'status': {'value': 'active'},
            'serial': 'DEF456'
        },
        {
            'id': 3,
            'name': 'nyc-fw01',
            'device_type': {'model': 'Palo Alto PA-3020'},
            'device_role': {'name': 'firewall'},
            'site': {'name': 'NYC'},
            'status': {'value': 'active'},
            'serial': 'GHI789'
        }
    ]