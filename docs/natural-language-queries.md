# Natural Language Queries for NetBox MCP

This document explains how the natural language processing capabilities work in the NetBox MCP server.

## Overview

The NetBox MCP server includes functionality to parse natural language queries about network devices and convert them into structured API calls to NetBox. This allows AI assistants or users to ask questions in plain English rather than constructing complex API parameters.

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

## Combined Queries

The processor can handle combined queries with multiple parameters:

```
"Show me all active firewalls at site SF1"
"List the first 10 offline switches in NYC1"
"Show me all wireless access points with Cisco model"
```

## Error Handling

When the query contains parameters that don't match NetBox data:

1. **Site Not Found**: The processor attempts fuzzy matching with case-insensitive searches. If no match is found, it returns a helpful error message suggesting available sites.

2. **Role Not Found**: The processor attempts fuzzy matching. If no match is found, it returns an error message suggesting using more generic terms.

## Implementation Details

The query processing happens in multiple stages:

1. **Text Parsing**: Regular expressions extract key information from the query
2. **Parameter Adaptation**: Extracted values are mapped to NetBox API parameters
3. **ID Resolution**: Names are converted to IDs where needed (e.g., site name to site_id)
4. **Fuzzy Matching**: Case-insensitive searches are used when exact matches fail
5. **API Query**: Structured parameters are sent to the NetBox API

## Example Usage

To query devices using natural language:

```bash
mcptools call ask_about_devices --params '{"query":{"query":"Show me all switches at site SF1"}}' python src/server.py
```