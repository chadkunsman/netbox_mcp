# NetBox MCP Server

A comprehensive read-only FastMCP server that exposes NetBox API functionality to AI systems via the Model Context Protocol (MCP).

## Overview

This project implements a read-only MCP server that provides comprehensive tools to interact with NetBox infrastructure data. It enables natural language queries about network devices, sites, circuits, VLANs, and IP prefixes, making it easier for AI assistants to retrieve and present network infrastructure information without allowing any modifications to the NetBox data.

## Features

### Device Management
- Query NetBox devices using structured filters
- Search for devices by specific name
- Use natural language to ask about devices
- Support for filtering by site, role, status, manufacturer, and more

### Site Operations
- List all available sites with status and region information
- Get comprehensive site details including device and rack counts
- Site-based filtering across all resource types

### Circuit Management
- Query circuits by provider, type, status, and termination sites
- Search circuits using natural language
- Track circuit terminations (A-side and Z-side)
- Filter by circuit ID patterns

### IP Prefix Management
- Query IP prefixes by site, VRF, tenant, status, and role
- Support for both IPv4 and IPv6 address families
- VLAN association and filtering
- Prefix pool management
- CIDR notation pattern matching

### VLAN Management
- Query VLANs by name, VID (VLAN ID), site, group, tenant, role, and status
- True substring matching for VLAN names and descriptions
- Cross-field search across VLAN properties
- Support for VLAN group and tenant organization

### Natural Language Processing
- Intelligent parsing of natural language queries into structured API calls
- Fuzzy matching for sites, roles, providers, and circuit types
- Cross-field search capabilities
- User-friendly error messages and suggestions

## Example Queries

### Device Queries
- "Show me all devices at site SF1"
- "List all active firewalls"
- "Tell me about device sf1.as1"
- "Find all ION devices"
- "Show switches at NYC location"

### Site Queries
- "List all available sites"
- "Tell me about site SF1"
- "Show site information for Denver"

### Circuit Queries
- "Show me circuits from Zayo"
- "List Internet circuits at SF1"
- "Find circuit CID-12345"
- "Show active MPLS circuits"

### IP Prefix Queries
- "Show IPv4 prefixes at SF1"
- "List all /24 subnets"
- "Find prefixes in VLAN 100"
- "Show prefix pools"

### VLAN Queries
- "Show me VLAN 100"
- "List all VLANs at site SF1"
- "Find VLANs with '90' in the name"
- "Show active VLANs for tenant ABC"
- "Get all production VLANs"

## Installation

### Using uvx (Recommended)

The easiest way to use this MCP server is with `uvx`:

```bash
# Install and run with environment variables
uvx --from . \
  --with-editable . \
  --env NETBOX_URL=https://your-netbox.example.com \
  --env NETBOX_TOKEN=your_api_token \
  --env NETBOX_SSL_VERIFY=true \
  netbox-mcp-server
```

### Development Setup

For development and testing:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/netbox-mcp.git
   cd netbox-mcp
   ```

2. Install in development mode:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. Set environment variables:
   ```bash
   export NETBOX_URL=https://your-netbox.example.com
   export NETBOX_TOKEN=your_api_token
   export NETBOX_SSL_VERIFY=true
   ```

### Claude Desktop Configuration

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "netbox": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/yourusername/netbox-mcp.git",
        "--with-editable", ".",
        "netbox-mcp-server"
      ],
      "env": {
        "NETBOX_URL": "https://your-netbox.example.com",
        "NETBOX_TOKEN": "your_api_token",
        "NETBOX_SSL_VERIFY": "true"
      }
    }
  }
}
```

### Testing with MCPTools

For development and testing, use MCPTools:

```bash
# List all available tools 
mcp tools uv run --directory src python server.py

# Call a specific tool with parameters
mcp call get_device --params '{"name":"my-device-01"}' uv run --directory src python server.py

# Start interactive testing shell
mcp shell uv run --directory src python server.py

# View server logs during testing
mcp tools --server-logs uv run --directory src python server.py
```

## Configuration

The server requires the following environment variables:

- `NETBOX_URL`: URL of your NetBox instance (e.g., https://netbox.example.com)
- `NETBOX_TOKEN`: API token with appropriate permissions
- `NETBOX_SSL_VERIFY`: Whether to verify SSL certificates (true/false)
- `DEBUG`: Enable debug mode (true/false)
- `LOG_LEVEL`: Logging level (info, debug, warning, error)

## Project Structure

```
netbox-mcp/
├── src/
│   ├── server.py          # Main MCP server implementation
│   ├── tools/             # Tool definitions
│   │   ├── devices.py     # Device-related tools
│   │   ├── sites.py       # Site-related tools
│   │   ├── circuits.py    # Circuit-related tools
│   │   ├── prefixes.py    # IP prefix-related tools
│   │   └── vlans.py       # VLAN-related tools
│   ├── models/            # Pydantic models
│   │   ├── device.py      # Device-related models
│   │   ├── site.py        # Site-related models
│   │   ├── circuit.py     # Circuit-related models
│   │   ├── prefix.py      # IP prefix-related models
│   │   └── vlan.py        # VLAN-related models
│   └── config/            # Configuration
│       └── netbox.py      # NetBox client configuration
├── docs/                  # Documentation
└── tests/                 # Test files
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.