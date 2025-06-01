"""
NetBox API client configuration.
"""

import os
import pynetbox
from typing import Optional

def get_netbox_client() -> pynetbox.api:
    """
    Initialize and return a configured NetBox API client.
    
    Returns a read-only client that can only perform GET requests
    to prevent any modifications to NetBox data.
    
    Returns:
        pynetbox.api: Configured NetBox API client
    
    Raises:
        EnvironmentError: If required environment variables are not set
    """
    url = os.getenv("NETBOX_URL")
    token = os.getenv("NETBOX_TOKEN")
    
    if not url:
        raise EnvironmentError("NETBOX_URL environment variable is not set")
    
    if not token:
        raise EnvironmentError("NETBOX_TOKEN environment variable is not set")
    
    # Create the client
    nb = pynetbox.api(url=url, token=token)
    
    # Configure SSL verification if specified
    ssl_verify = os.getenv("NETBOX_SSL_VERIFY", "true").lower() in ("true", "1", "t")
    
    # Create a custom session with SSL verification setting
    import requests
    session = requests.Session()
    session.verify = ssl_verify
    
    # Create a custom adapter that enforces GET requests only
    from requests.adapters import HTTPAdapter
    class ReadOnlyAdapter(HTTPAdapter):
        def send(self, request, **kwargs):
            if request.method.upper() != 'GET':
                raise ValueError(f"This is a read-only client. Method '{request.method}' is not allowed.")
            return super().send(request, **kwargs)
    
    # Mount the adapter to all requests
    read_only_adapter = ReadOnlyAdapter()
    session.mount('http://', read_only_adapter)
    session.mount('https://', read_only_adapter)
    
    # Assign the session to the client
    nb.http_session = session
    
    return nb