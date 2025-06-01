# NetBox MCP Examples

This directory contains example scripts and commands for using the NetBox MCP server.

## MCPTools Commands

The `mcptools_commands.sh` script contains example commands for testing the NetBox MCP server with MCPTools. Here are some key examples:

### List Available Tools

```bash
mcptools tools python src/server.py
```

Output example:
```
get_devices(filter_params:)
     Get devices from NetBox based on filter parameters...

get_device(name:str)
     Get a specific device by name...

ask_about_devices(query:)
     Query devices using natural language...
```

### Query All Devices with a Filter

```bash
mcptools call get_devices --params '{"filter_params":{"site":"SF1","limit":5}}' python src/server.py
```

### Get a Specific Device

```bash
mcptools call get_device --params '{"name":"as1.sf1"}' python src/server.py 
```

Example output:
```json
{
  "id": 2116,
  "name": "as1.sf1",
  "site": "SF1",
  "role": "office_access_switch",
  "status": "active",
  "model": "C9300-48P",
  "ip_address": "10.255.10.13",
  "serial": "FCW2329G083",
  "description": "",
  "tags": []
}
```

### Use Natural Language Queries

```bash
mcptools call ask_about_devices --params '{"query":{"query":"Show me all switches at site SF1"}}' python src/server.py
```

This will return a list of all office_access_switch devices at site SF1.

### Interactive Testing

For interactive testing, use the shell mode:

```bash
mcptools shell python src/server.py
```

## Common Query Examples

### Site-Based Queries

```bash
# All devices at SF1 site
mcptools call ask_about_devices --params '{"query":{"query":"Show me all devices at site SF1"}}' python src/server.py

# All devices at NYC1 site
mcptools call ask_about_devices --params '{"query":{"query":"List devices in NYC1 location"}}' python src/server.py
```

### Role-Based Queries

```bash
# All switches
mcptools call ask_about_devices --params '{"query":{"query":"Show me all switches"}}' python src/server.py

# All access points
mcptools call ask_about_devices --params '{"query":{"query":"List all wireless access points"}}' python src/server.py
```

### Combined Queries

```bash
# Active switches at SF1
mcptools call ask_about_devices --params '{"query":{"query":"Show me all active switches at site SF1"}}' python src/server.py

# Limited results
mcptools call ask_about_devices --params '{"query":{"query":"Show me the first 5 switches at NYC1"}}' python src/server.py
```

## Environment Setup

Make sure to set the required environment variables before running the examples:

```bash
export NETBOX_URL="https://your-netbox-instance.com"
export NETBOX_TOKEN="your_api_token"
export NETBOX_SSL_VERIFY="true"
```

Or create a `.env` file in the project root directory with these variables.