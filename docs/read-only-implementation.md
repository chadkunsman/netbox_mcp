# Read-Only Implementation Guide

This document explains how the read-only enforcement is implemented in the NetBox MCP server.

## Overview

The NetBox MCP server is designed as strictly read-only to ensure that AI systems or other clients can query information about network devices but cannot make any modifications to the NetBox data. This is implemented through multiple layers of protection.

## Custom HTTP Adapter

The primary enforcement mechanism is a custom `ReadOnlyAdapter` that inherits from `requests.adapters.HTTPAdapter`. This adapter is used to intercept all HTTP requests made through the PyNetBox client:

```python
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
```

## How It Works

1. **Request Interception**: The adapter's `send` method intercepts every HTTP request before it's sent.

2. **Method Validation**: The method of each request is checked. If it's not a `GET` request, a `ValueError` is raised.

3. **Exception Handling**: Any attempt to use methods like `POST`, `PUT`, `PATCH`, or `DELETE` that would modify data will immediately fail.

4. **Session Assignment**: The adapter is mounted for all HTTP and HTTPS requests made through the session assigned to the NetBox client.

## Benefits of This Approach

- **Low-Level Enforcement**: The protection happens at the HTTP request level, which is more secure than application-level checks.
- **Comprehensive Coverage**: All potential write operations are blocked, regardless of which API endpoint is accessed.
- **Fail-Safe Design**: Even if code is added later that attempts to modify data, the adapter will prevent it.
- **Transparency**: Clear error messages explain why modifications are not allowed.

## Testing Read-Only Enforcement

The read-only implementation can be tested by attempting to modify data:

```python
try:
    # This should fail due to the ReadOnlyAdapter
    nb.dcim.devices.create(name="test-device", device_type=1, site=1)
except ValueError as e:
    print(f"Verification successful: {e}")
```

## Security Considerations

While the read-only adapter provides strong protection against accidental modifications, there are additional security considerations:

1. **API Token Permissions**: The NetBox API token used should also have read-only permissions in NetBox itself as a second layer of protection.

2. **Token Rotation**: API tokens should be rotated regularly according to security best practices.

3. **Environment Variables**: The token should only be provided through environment variables, never hardcoded.

4. **SSL Verification**: SSL certificate verification should be enabled in production to prevent man-in-the-middle attacks.

## Example Environment Configuration

```bash
NETBOX_URL=https://netbox.example.com
NETBOX_TOKEN=read_only_token_here
NETBOX_SSL_VERIFY=true
```