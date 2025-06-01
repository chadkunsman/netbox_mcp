# Natural Language Queries for NetBox MCP

This document explains how the natural language processing capabilities work in the NetBox MCP server.

## Overview

The NetBox MCP server includes functionality to parse natural language queries about network devices, circuits, and IP prefixes and convert them into structured API calls to NetBox. This allows AI assistants or users to ask questions in plain English rather than constructing complex API parameters.

## Query Capabilities

The natural language processor can extract the following types of information from queries:

### Site Information
```
"Show me all devices at site SF1"
"List devices in NYC1 location"
"Get devices from DEN1 site"
```

The processor identifies site names from common patterns like:
- "at site X"
- "in X location"
- "from X site"

### Device Role Information
```
"Show me all switches"
"List all firewalls"
"Get all wireless access points"
```

The processor maps common terms to NetBox device roles:
- "switch" → `office_access_switch`
- "firewall" → `net-firewall`
- "wireless" or "accesspoint" or "ap" → `net-wireless-accesspoint`
- "router" → `router`
- "server" → `server`

### Device Status
```
"Show active devices"
"List planned devices"
"Get offline devices"
```

The processor can filter by status:
- "active" → `active`
- "planned" → `planned`
- "staged" → `staged`
- "failed" → `failed`
- "offline" → `offline`

### Specific Device Queries
```
"Tell me about device as1.sf1"
"Show information on device nyc1-sw01"
"Get details for device core-fw01"
```

The processor recognizes queries about specific devices using patterns like:
- "about device X"
- "tell me about X"
- "information on X"
- "details for X"

### General Device Search
```
"Find all ION devices"
"Show me C9300 switches"
"List devices with model ASA"
```

For queries that don't match specific site/role/status patterns, the processor uses NetBox's general search functionality, which searches across device names, models, descriptions, and serial numbers. This provides a simple fallback for complex queries without requiring extensive pattern matching.

### Result Limits
```
"Show me the first 5 devices"
"List top 10 switches"
"Limit results to 20 devices"
```

The processor can apply result limits using patterns like:
- "first X"
- "top X"
- "limit X"

## IP Prefix Queries

The natural language processor also supports prefix/IPAM queries:

### IP Family Queries
```
"Show me all IPv4 prefixes"
"List IPv6 prefixes"  
"Find all v4 subnets"
```

### VLAN-Based Queries
```
"Show me prefixes with VLAN 100"
"List prefixes for vlan exchange-100"
"Find prefixes associated with VID 25"
"Get prefixes for VLAN production"
```

### Prefix Status Queries
```
"Show active prefixes"
"List reserved prefix pools"
"Get deprecated prefixes"
"Find container prefixes"
```

### Site-Based Prefix Queries
```
"Show me all prefixes at site SF1"
"List prefixes in NYC1 location"
"Get IPv4 prefixes from DEN1 site"
```

## Combined Queries

The processor can handle combined queries with multiple parameters:

### Device Queries
```
"Show me all active firewalls at site SF1"
"List the first 10 offline switches in NYC1"
"Show me all wireless access points with Cisco model"
```

### Prefix Queries
```
"Show me IPv4 prefixes with VLAN 100 at site NYC1"
"List active prefix pools at site SF1"
"Find reserved IPv6 prefixes in VRF production"
"Get office management prefixes with VLAN exchange-100"
```

## Error Handling

When the query contains parameters that don't match NetBox data:

1. **Site Not Found**: The processor attempts fuzzy matching with case-insensitive searches. If no match is found, it returns a helpful error message suggesting available sites.

2. **Role Not Found**: The processor attempts fuzzy matching. If no match is found, it returns an error message suggesting using more generic terms.

3. **VLAN Not Found**: For prefix queries, the processor attempts to find VLANs by ID, VID, or name. If no match is found, it returns an error message indicating the VLAN was not found.

## Implementation Details

The query processing uses a simplified approach:

1. **Structured Parameter Extraction**: Regular expressions extract site, role, and status information
2. **General Search Fallback**: If no specific parameters are found, the entire query is sent to NetBox's general search (`q` parameter)
3. **Parameter Adaptation**: Extracted values are mapped to NetBox API parameters  
4. **ID Resolution**: Names are converted to IDs where needed (e.g., site name to site_id)
5. **Fuzzy Matching**: Case-insensitive searches are used when exact matches fail
6. **API Query**: Structured parameters are sent to the NetBox API

This approach prioritizes simplicity and leverages NetBox's built-in search capabilities rather than complex pattern matching.

## Example Usage

### Device Queries
To query devices using natural language:

```bash
# Specific site/role queries
mcp call ask_about_devices --params '{"query":{"query":"Show me all switches at site SF1"}}' uv run --directory src python server.py

# General search queries (uses NetBox's built-in search)
mcp call ask_about_devices --params '{"query":{"query":"find all ION devices"}}' uv run --directory src python server.py
```

Or use structured parameters for more control:

```bash
# Pattern matching for device names
mcp call get_devices --params '{"filter_params":{"name_contains":"ion","limit":20}}' uv run --directory src python server.py

# Cross-field search
mcp call get_devices --params '{"filter_params":{"search":"ION","limit":20}}' uv run --directory src python server.py
```

### Prefix Queries
To query prefixes using natural language:

```bash
# Specific site/family queries
mcp call ask_about_prefixes_tool --params '{"query":{"query":"Show me IPv4 prefixes with VLAN 100 at site NYC1"}}' uv run --directory src python server.py

# General search queries (uses NetBox's built-in search)
mcp call ask_about_prefixes_tool --params '{"query":{"query":"find office prefixes"}}' uv run --directory src python server.py
```

Or use structured parameters for more control:

```bash
# Cross-field search
mcp call get_prefixes_tool --params '{"filter_params":{"search":"192.168","limit":10}}' uv run --directory src python server.py

# IPv4/IPv6 family filtering
mcp call get_prefixes_tool --params '{"filter_params":{"family":4,"limit":20}}' uv run --directory src python server.py
```

### Circuit Queries
To query circuits using natural language:

```bash
# Specific provider/type queries
mcp call ask_about_circuits --params '{"query":{"query":"Show me all internet circuits from provider Zayo"}}' uv run --directory src python server.py

# General search queries (uses NetBox's built-in search)
mcp call ask_about_circuits --params '{"query":{"query":"find all Lumen circuits"}}' uv run --directory src python server.py
```

Or use structured parameters for more control:

```bash
# Pattern matching for circuit IDs
mcp call get_circuits --params '{"filter_params":{"cid_contains":"346","limit":10}}' uv run --directory src python server.py

# Cross-field search
mcp call get_circuits --params '{"filter_params":{"search":"Zayo","limit":10}}' uv run --directory src python server.py
```