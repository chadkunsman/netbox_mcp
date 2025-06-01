# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a read-only FastMCP server that exposes NetBox API functionality to AI systems via the Model Context Protocol (MCP). The server provides comprehensive access to devices, sites, and circuits, enabling natural language queries about network infrastructure in a NetBox instance without allowing any modifications to the NetBox data.

FastMCP servers act as bridges between AI applications (like Claude, ChatGPT) and your APIs or services, allowing AI systems to discover and use your tools intelligently.

## Implementation Notes

The server strictly enforces read-only access through a custom `ReadOnlyAdapter` that blocks any non-GET HTTP requests to the NetBox API. This ensures that AI systems can query device information but cannot make any changes to the infrastructure data.

### Available Tools

The MCP server provides eight main tools:

**Device Tools:**
1. `get_devices`: Accepts structured filter parameters to query devices with specific attributes
2. `get_device`: Retrieves detailed information about a single device by name
3. `ask_about_devices`: Accepts natural language queries and converts them to appropriate API calls

**Site Tools:**
4. `get_sites`: Lists all available sites with basic information (name, status, region)
5. `get_site_info`: Retrieves comprehensive information about a specific site including device/rack counts

**Circuit Tools:**
6. `get_circuits`: Accepts structured filter parameters to query circuits with specific attributes
7. `get_circuit`: Retrieves detailed information about a single circuit by CID (Circuit ID)
8. `ask_about_circuits`: Accepts natural language queries and converts them to appropriate circuit API calls

### Natural Language Processing

The server includes intelligent parsing of natural language queries into structured NetBox API parameters. It can:

**Device Queries:**
- Extract site names (e.g., "SF1", "NYC1", "DEN1")
- Identify device roles (e.g., "office_access_switch", "net-wireless-accesspoint")
- Understand queries about specific devices
- Handle fuzzy matches for site names and roles using NetBox's search capabilities

**Circuit Queries:**
- Extract circuit IDs (e.g., "CID-12345", "346513905")
- Identify providers (e.g., "Zayo", "Lumen", "Verizon")
- Recognize circuit types (e.g., "Internet", "MPLS", "Point-to-Point")
- Filter by termination sites (both A-side and Z-side terminations)
- Parse status filters (e.g., "active", "provisioning", "decommissioned")

**General Features:**
- Provide user-friendly error messages when parameters don't match NetBox's data
- Support fuzzy matching for providers, circuit types, and site names

## Quick Commands

### Testing MCP Servers

Use MCPTools to test any MCP server implementation:

```bash
# List all available tools 
mcp tools uv run --directory src python server.py

# Call a specific tool with parameters
mcp call <tool-name> --params '{"param1":"value1"}' uv run --directory src python server.py

# Start interactive testing shell
mcp shell uv run --directory src python server.py

# View server logs during testing
mcp tools --server-logs uv run --directory src python server.py
```

**Note**: Do not start the server separately. MCPTools will start it and communicate with it via stdio.

### Package Management

```bash
# Install dependencies manually
uv pip install -e .

# Add a new dependency
uv add <package_name>
```

**Important**: For proper MCP server launching with UV, add this to your `pyproject.toml`:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

## Essential FastMCP Patterns

### Basic Server Setup
```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
async def example_tool(parameter: str) -> dict:
    """Tool documentation here."""
    return {"result": "value"}

if __name__ == "__main__":
    mcp.run()
```

### Input Validation with Pydantic
```python
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')

@mcp.tool()
def create_user(request: UserRequest) -> dict:
    """Create user with validated input."""
    return {"user_id": "123", "name": request.name}
```

### Error Handling
```python
from fastmcp.exceptions import ToolError

@mcp.tool()
def safe_tool(param: str) -> str:
    try:
        # Your tool logic
        return result
    except ValueError as e:
        # Client sees generic error
        raise ValueError("Invalid input")
    except SomeError as e:
        # Client sees specific error
        raise ToolError(f"Tool failed: {str(e)}")
```

### Authentication Context
```python
from fastmcp import Context

@mcp.tool()
async def authenticated_tool(param: str, ctx: Context) -> dict:
    """Tool requiring authentication."""
    user_id = ctx.client_id
    scopes = ctx.scopes
    
    if "required_scope" not in scopes:
        raise ToolError("Insufficient permissions")
    
    return {"result": f"Hello user {user_id}"}
```

## Key Development Workflow

1. **Create Tools**: Define functions with `@mcp.tool()` decorator
2. **Test Locally**: Use `mcp tools uv run --directory src python server.py` to verify tools work
3. **Add Validation**: Use Pydantic models for input validation
4. **Handle Errors**: Use `ToolError` for client-visible errors
5. **Test Integration**: Use `mcp shell uv run --directory src python server.py` for interactive testing
6. **Deploy**: Configure for production deployment

## MCP Server Types

- **Local Servers**: Run as subprocesses, communicate via STDIO, good for file system access
- **Remote Servers**: Run as web services, support OAuth 2.1, better for SaaS integrations

## Transport Protocols

- **STDIO**: For local servers (subprocess communication)
- **Streamable HTTP**: Modern protocol for remote servers (recommended)
- **HTTP+SSE**: Legacy protocol for backward compatibility

## Project Structure

```
src/
├── server.py          # Main MCP server implementation
├── tools/             # Tool definitions for NetBox operations
│   ├── devices.py     # Device-related tools and logic
│   ├── sites.py       # Site-related tools and logic
│   └── circuits.py    # Circuit-related tools and logic
├── models/            # Pydantic models for validation
│   ├── device.py      # Device model definitions
│   ├── site.py        # Site model definitions
│   └── circuit.py     # Circuit model definitions
└── config/            # Configuration and settings
    └── netbox.py      # NetBox client configuration
```

## Essential Dependencies

- `fastmcp` - MCP server framework
- `pydantic` - Data validation and models
- `pynetbox` - Python client library for NetBox API
- `python-dotenv` - Environment variable management

## Functional Focus

The NetBox MCP server specifically focuses on:
1. **Device Queries**: Searching and filtering devices by various attributes
2. **Site Information**: Comprehensive site details including infrastructure counts
3. **Site-Based Filtering**: Finding devices and circuits at specific sites
4. **Device Role Filtering**: Identifying devices by their role (e.g., firewall, switch)
5. **Circuit Management**: Querying circuits by provider, type, status, and termination sites
6. **Circuit Termination Tracking**: Finding circuits that terminate at specific sites (A-side or Z-side)
7. **Natural Language Understanding**: Converting natural language queries to structured API calls
8. **Readable Responses**: Formatting device, site, and circuit data in an easy-to-understand way

## Environment Variables

Key configuration variables:
```bash
NETBOX_URL=https://netbox.example.com      # NetBox API URL
NETBOX_TOKEN=abcdef123456                  # NetBox API authentication token
NETBOX_SSL_VERIFY=true                     # Whether to verify SSL certificates
DEBUG=false                                # Debug mode
LOG_LEVEL=info                             # Logging level
```

## Virtual Environment Setup

The project uses UV for Python environment management:

```bash
# Create virtual environment
uv venv

# Activate the environment
source .venv/bin/activate

# Install dependencies
uv pip install fastmcp pynetbox pydantic python-dotenv
```

## Common NetBox Device Roles

Based on our exploration of the NetBox instance, common device roles include:
- `office_access_switch` - Access switches (not just "switch")
- `net-wireless-accesspoint` - Wireless access points
- `net-firewall` - Firewalls
- `router` - Routers
- `net-structured-cabling` - Cabling equipment
- `net-facilities-pdu` - Power distribution units
- `net-monitoring` - Network monitoring devices

## Testing with MCPTools

```bash
# List all tools
mcp tools uv run --directory src python server.py

# Device Operations
# Query devices with natural language
mcp call ask_about_devices --params '{"query":{"query":"Show me all switches at site SF1"}}' uv run --directory src python server.py

# Get a specific device
mcp call get_device --params '{"name":"as1.sf1"}' uv run --directory src python server.py 

# Filter devices using structured parameters
mcp call get_devices --params '{"filter_params":{"site":"SF1","limit":5}}' uv run --directory src python server.py

# Site Operations
# List all available sites
mcp call get_sites --params '{"limit":20}' uv run --directory src python server.py

# Get comprehensive site information
mcp call get_site_info --params '{"name":"SF1"}' uv run --directory src python server.py

# Circuit Operations
# Query circuits with natural language
mcp call ask_about_circuits --params '{"query":{"query":"Show me circuits at site SF1"}}' uv run --directory src python server.py

# Get a specific circuit by CID
mcp call get_circuit --params '{"cid":"346513905"}' uv run --directory src python server.py

# Filter circuits using structured parameters
mcp call get_circuits --params '{"filter_params":{"provider":"Zayo","type":"Internet","limit":10}}' uv run --directory src python server.py

# Find circuits by site termination
mcp call get_circuits --params '{"filter_params":{"site":"SF1","limit":10}}' uv run --directory src python server.py
```

## Troubleshooting

- **Tool not found**: Check tool is registered with `@mcp.tool()` decorator
- **Validation errors**: Verify Pydantic model matches expected NetBox data structure
- **Authentication issues**: Check NetBox token validity and permissions
- **Connection issues**: Verify NetBox URL is accessible
- **Role/site not found**: Make sure you're using the exact roles/sites from NetBox (e.g., `office_access_switch`, not just `switch`)
- **Testing failures**: Use `mcp tools --server-logs` to see detailed errors
- **Import errors**: When running from src directory, use relative imports (not using `src.` prefix)
- **Setup issues**: Check if dependencies are installed in your virtual environment