# NetBox Prefixes API Documentation

This document provides a reference for the NetBox API endpoints related to IP prefixes that are used by the NetBox MCP Server.

## Overview

The NetBox MCP server provides comprehensive access to IP Address Management (IPAM) functionality through prefix-related tools. These tools allow querying and filtering IP prefixes (CIDR blocks) across various dimensions including sites, VRFs, tenants, and status.

## Available Prefix Tools

The MCP server provides three main prefix tools:

### 1. `get_prefixes_tool`
Retrieves prefixes using structured filter parameters.

### 2. `get_prefix_tool` 
Gets detailed information about a specific prefix by ID.

### 3. `ask_about_prefixes_tool`
Processes natural language queries about prefixes.

## Prefix Endpoints

### List Prefixes

```
GET /api/ipam/prefixes/
```

Retrieves a list of IP prefixes. Can be filtered by various parameters.

#### Filter Parameters:

- **prefix**: Specific IP prefix (e.g., '192.168.1.0/24', '10.0.0.0/8')
- **site**: Site name or ID  
- **vrf**: VRF name or ID
- **tenant**: Tenant name or ID
- **vlan**: VLAN name, ID, or VID (e.g., 'exchange-100', '25', '100')
- **status**: Prefix status (active, reserved, deprecated, container)
- **role**: Prefix role name or ID
- **family**: IP family (4 for IPv4, 6 for IPv6)
- **is_pool**: Whether the prefix is a pool (true/false)
- **tag**: Tag name
- **limit**: Maximum number of results (default: 50, max: 1000)

#### Example Request:

```bash
curl -X GET \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; indent=4" \
  http://netbox/api/ipam/prefixes/?site_id=6&family=4&status=active&vlan_id=25
```

#### Example Response:

```json
{
  "count": 18,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 936,
      "url": "http://netbox/api/ipam/prefixes/936/",
      "family": {
        "value": 4,
        "label": "IPv4"
      },
      "prefix": "10.114.0.0/18",
      "site": {
        "id": 6,
        "url": "http://netbox/api/dcim/sites/6/",
        "name": "SF1",
        "slug": "sf1"
      },
      "vrf": null,
      "tenant": {
        "id": 2,
        "name": "Gusto NetEng"
      },
      "vlan": {
        "id": 25,
        "url": "http://netbox/api/ipam/vlans/25/",
        "name": "exchange-100",
        "vid": 100
      },
      "status": {
        "value": "container",
        "label": "Container"
      },
      "role": null,
      "is_pool": false,
      "description": "USSFO1 ( 525 20th St, San Francisco, CA 94107)",
      "tags": [],
      "custom_fields": {},
      "created": "2020-11-30T00:00:00Z",
      "last_updated": "2024-12-10T22:31:24.733107Z"
    }
  ]
}
```

### Get Specific Prefix

```
GET /api/ipam/prefixes/{id}/
```

Retrieves a specific prefix by ID.

#### Example Request:

```bash
curl -X GET \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; indent=4" \
  http://netbox/api/ipam/prefixes/936/
```

## Common Fields in Prefix Objects

- **id**: Unique identifier for the prefix
- **prefix**: IP prefix in CIDR notation (e.g., "10.114.0.0/18")
- **family**: IP version object (IPv4 or IPv6)
- **site**: Reference to the site object (if assigned)
- **vrf**: Reference to the VRF object (if assigned) 
- **tenant**: Reference to the tenant object (if assigned)
- **vlan**: Reference to the VLAN object (if assigned)
- **status**: Prefix status object (active, reserved, deprecated, container)
- **role**: Reference to the prefix role object (if assigned)
- **is_pool**: Boolean indicating if this is a pool prefix
- **description**: Description text
- **tags**: List of associated tags
- **utilization**: Percentage of IP addresses used (if calculated)
- **available_ips**: Number of available IP addresses
- **created**: Creation timestamp
- **last_updated**: Last modification timestamp

## Natural Language Query Examples

The `ask_about_prefixes_tool` can understand various natural language patterns:

### Site-Based Queries
```
"Show me all prefixes at site SF1"
"List prefixes in NYC1 location"  
"Get prefixes from DEN1 site"
```

### IP Family Queries
```
"Show me all IPv4 prefixes"
"List IPv6 prefixes"
"Find all v4 subnets"
```

### Status-Based Queries
```
"Show active prefixes"
"List reserved prefixes"
"Get deprecated prefix pools"
```

### Role-Based Queries
```
"Show office management prefixes"
"List internet transport prefixes"
"Find out-of-band management prefixes"
```

### VLAN-Based Queries
```
"Show me prefixes with VLAN 100"
"List prefixes for vlan exchange-100"
"Find prefixes associated with VID 25"
"Get prefixes for VLAN production"
```

### Combined Queries
```
"Show me all IPv4 prefixes at site SF1"
"List active prefixes in VRF production"
"Find reserved prefix pools"
"Get office management prefixes for tenant ABC"
"Show me IPv4 prefixes with VLAN 100 at site NYC1"
"Find active prefixes for VLAN exchange-100"
```

## Testing with MCPTools

```bash
# List all tools
mcp tools uv run --directory src python server.py

# Prefix Operations
# Query prefixes with natural language
mcp call ask_about_prefixes_tool --params '{"query":{"query":"Show me all IPv4 prefixes at site SF1"}}' uv run --directory src python server.py

# Get a specific prefix by ID
mcp call get_prefix_tool --params '{"prefix_id":936}' uv run --directory src python server.py

# Filter prefixes using structured parameters
mcp call get_prefixes_tool --params '{"filter_params":{"site":"SF1","family":4,"limit":10}}' uv run --directory src python server.py

# Find prefixes by VLAN
mcp call get_prefixes_tool --params '{"filter_params":{"vlan":"100","site":"SF1","limit":10}}' uv run --directory src python server.py

# Find prefixes by status
mcp call get_prefixes_tool --params '{"filter_params":{"status":"active","is_pool":true,"limit":20}}' uv run --directory src python server.py

# Search for specific prefix ranges
mcp call ask_about_prefixes_tool --params '{"query":{"query":"Find all /24 subnets"}}' uv run --directory src python server.py

# Query by VLAN
mcp call ask_about_prefixes_tool --params '{"query":{"query":"Show me prefixes with VLAN 100"}}' uv run --directory src python server.py

# Combined VLAN, family, and site query
mcp call ask_about_prefixes_tool --params '{"query":{"query":"Show me IPv4 prefixes with VLAN 100 at site NYC1"}}' uv run --directory src python server.py
```

## Common Prefix Roles

Based on exploration of the NetBox instance, common prefix roles include:
- `office-internet-transport` - Internet connectivity prefixes
- `office-management` - Management network prefixes  
- `office-ap` - Access point network prefixes
- `office-guest-wifi` - Guest wireless network prefixes
- `office-guest-wire` - Guest wired network prefixes
- `office-print` - Printer network prefixes
- `office-services` - Services network prefixes
- `office-physical-security` - Physical security device prefixes
- `office-signage` - Digital signage network prefixes
- `office-av` - Audio/visual equipment prefixes
- `office-zoom` - Video conferencing equipment prefixes
- `office-bms` - Building management system prefixes
- `office-iot` - IoT device network prefixes
- `office-oob-transport` - Out-of-band transport prefixes
- `out-of-band-management` - Out-of-band management prefixes
- `network-exchange` - Network peering/exchange prefixes
- `net-route-public` - Public routing prefixes
- `net-route-wan` - WAN routing prefixes
- `net-endpoints-dmz` - DMZ endpoint prefixes

## Common Status Values

- **Active**: Prefix is actively in use
- **Reserved**: Prefix is reserved for future use
- **Deprecated**: Prefix is being phased out
- **Container**: Prefix contains smaller subnets

## Useful Query Parameters

- **?limit=value**: Number of objects to return (default: 50, max: 1000)
- **?offset=value**: The initial index from which to return results
- **?prefix=value**: Exact prefix match
- **?prefix__net_contains=value**: Find prefixes containing a specific IP/prefix
- **?prefix__net_contained_by=value**: Find prefixes contained within a larger prefix
- **?site=value**: Filter by site name
- **?site_id=value**: Filter by site ID
- **?family=value**: Filter by IP family (4 or 6)
- **?status=value**: Filter by status
- **?is_pool=value**: Filter by pool status (true/false)
- **?vrf=value**: Filter by VRF name
- **?vlan=value**: Filter by VLAN name
- **?vlan_id=value**: Filter by VLAN ID
- **?tenant=value**: Filter by tenant name

## Sample API Response (Python)

Using pynetbox, you can access prefix data as follows:

```python
import pynetbox

nb = pynetbox.api(
    'http://netbox.example.com',
    token='abcdef123456'
)

# Get all prefixes
prefixes = nb.ipam.prefixes.all()

# Filter prefixes by site
site_prefixes = nb.ipam.prefixes.filter(site='sf1')

# Get prefixes by family
ipv4_prefixes = nb.ipam.prefixes.filter(family=4)

# Get prefixes by VLAN
vlan_prefixes = nb.ipam.prefixes.filter(vlan_id=25)

# Get a specific prefix by ID
prefix = nb.ipam.prefixes.get(936)

# Print prefix information
print(f"Prefix: {prefix.prefix}")
print(f"Site: {prefix.site.name if prefix.site else 'None'}")
print(f"VLAN: {prefix.vlan.name if prefix.vlan else 'None'}")
print(f"Status: {prefix.status}")
print(f"Role: {prefix.role.name if prefix.role else 'None'}")
print(f"Family: {prefix.family}")
```

## Error Handling

The prefix tools provide helpful error messages:

- **Site not found**: When a specified site doesn't exist, suggests checking the site name
- **Invalid parameters**: When filter parameters don't match expected formats
- **No results**: When queries return no matching prefixes
- **Connection issues**: When NetBox API is unreachable

## Integration with Other Tools

Prefix tools work seamlessly with other NetBox MCP tools:

- **Sites**: Prefixes can be filtered by site using the same site names as device and circuit tools
- **Cross-referencing**: Use site information from `get_sites` to discover available sites for prefix queries
- **Consistent formatting**: All tools follow the same response format patterns for easy integration