"""
NetBox MCP Server

A read-only FastMCP server that provides comprehensive tools for interacting with NetBox API.
This server supports devices, sites, circuits, and IP prefixes, enabling natural language 
queries about network infrastructure in a NetBox instance without allowing any modifications 
to the NetBox data.
"""

import os
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError

from models.device import DeviceFilterParameters, DeviceQuery, DeviceSummary
from models.site import SiteSummary, SiteBasic
from models.circuit import CircuitFilterParameters, CircuitQuery, CircuitSummary
from models.prefix import PrefixFilterParameters, PrefixQuery, PrefixSummary
from tools.devices import get_devices_by_filter, get_device_by_name, query_devices
from tools.sites import get_site_info_by_name, list_all_sites
from tools.circuits import get_circuits_by_filter, get_circuit_by_cid, query_circuits

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("NetBox MCP Server")

# Register tools
@mcp.tool()
async def get_devices(filter_params: DeviceFilterParameters, ctx: Context) -> list[DeviceSummary]:
    """
    Get devices from NetBox based on filter parameters.
    
    Available filters:
    - site: Filter by site name (e.g., "SF1", "NYC1")
    - role: Filter by device role (e.g., "office_access_switch", "net-firewall")
    - status: Filter by status (e.g., "active", "planned", "offline")
    - name: Exact device name
    - name_contains: Pattern matching for device names (case-insensitive)
    - search: Cross-field search across name, model, description, and serial
      IMPORTANT: Treats multiple words as AND (all must match). For OR logic, use separate calls.
      Example: "UPS PDU" requires BOTH "UPS" AND "PDU" in the same record - use separate calls for UPS OR PDU devices.
    - manufacturer: Filter by manufacturer name
    - model: Filter by model name
    - limit: Maximum number of results (default 50, max 1000)
    
    Search strategy recommendations:
    - For device types: Use separate calls (search="UPS", then search="PDU") rather than "UPS PDU"
    - For patterns: Use name_contains (e.g., name_contains="ion" finds all ION devices)
    - For models/descriptions: Use search with single terms for best results
    
    Args:
        filter_params: Parameters to filter devices by
        ctx: MCP context
    """
    return get_devices_by_filter(mcp, filter_params, ctx)

@mcp.tool()
async def get_device(name: str, ctx: Context) -> DeviceSummary:
    """
    Get a specific device by name.
    
    Returns detailed information about a single device.
    
    Args:
        name: Device name
        ctx: MCP context
    """
    return get_device_by_name(mcp, name, ctx)

@mcp.tool()
async def ask_about_devices(query: DeviceQuery, ctx: Context) -> list[DeviceSummary]:
    """
    Query devices using natural language.
    
    Examples:
        - "Show me all devices at site SF1"
        - "List all active firewalls"
        - "Tell me about device sf1.as1"
        - "Show the first 5 switches at NYC location"
    
    Args:
        query: Natural language query string
        ctx: MCP context
    """
    return query_devices(mcp, query, ctx)

@mcp.tool()
async def get_sites(limit: int = 50, ctx: Context = None) -> list[SiteBasic]:
    """
    List all sites with basic information.
    
    Returns a list of all sites in NetBox with basic details like name, status, 
    and region. Useful for discovering available sites before querying specific 
    site details.
    
    Args:
        limit: Maximum number of sites to return (default 50, max 1000)
        ctx: MCP context
    """
    # Validate limit
    if limit > 1000:
        limit = 1000
    elif limit < 1:
        limit = 1
    
    return list_all_sites(mcp, limit, ctx)

@mcp.tool()
async def get_site_info(name: str, ctx: Context) -> SiteSummary:
    """
    Get comprehensive information about a site including device and rack counts.
    
    Provides detailed site information including:
    - Basic site details (name, status, region, etc.)
    - Physical location information
    - Device count at the site
    - Rack count at the site
    
    Args:
        name: Site name
        ctx: MCP context
    """
    return get_site_info_by_name(mcp, name, ctx)

@mcp.tool()
async def get_circuits(filter_params: CircuitFilterParameters, ctx: Context) -> list[CircuitSummary]:
    """
    Get circuits from NetBox based on filter parameters.
    
    Available filters:
    - cid: Exact circuit ID
    - cid_contains: Pattern matching for circuit IDs (case-insensitive)
    - provider: Filter by provider name (e.g., "Zayo", "Lumen", "Verizon")
    - type: Filter by circuit type (e.g., "Internet", "MPLS", "Point-to-Point")
    - status: Filter by status (e.g., "active", "provisioning", "decommissioned")
    - site: Filter by termination site (both A-side and Z-side)
    - search: Cross-field search across CID, provider, description, and terminations
      IMPORTANT: Treats multiple words as AND (all must match). Use separate calls for OR logic.
    - limit: Maximum number of results (default 50, max 1000)
    
    Search strategy recommendations:
    - For multiple providers: Use separate calls rather than "Zayo Lumen" search
    - For circuit patterns: Use cid_contains for partial CID matching
    - For general search: Use single terms for best results
    
    Args:
        filter_params: Parameters to filter circuits by
        ctx: MCP context
    """
    return get_circuits_by_filter(mcp, filter_params, ctx)

@mcp.tool()
async def get_circuit(cid: str, ctx: Context) -> CircuitSummary:
    """
    Get a specific circuit by circuit ID (CID).
    
    Returns detailed information about a single circuit including provider,
    type, status, and termination sites.
    
    Args:
        cid: Circuit ID
        ctx: MCP context
    """
    return get_circuit_by_cid(mcp, cid, ctx)

@mcp.tool()
async def ask_about_circuits(query: CircuitQuery, ctx: Context) -> list[CircuitSummary]:
    """
    Query circuits using natural language.
    
    Examples:
        - "Show me all internet circuits"
        - "List all circuits from provider Verizon"
        - "Tell me about circuit CID-12345"
        - "Show active MPLS circuits at site SF1"
    
    Args:
        query: Natural language query string
        ctx: MCP context
    """
    return query_circuits(mcp, query, ctx)

@mcp.tool()
async def get_prefixes_tool(filter_params: PrefixFilterParameters, ctx: Context) -> dict:
    """
    Get prefixes from NetBox with filtering options.
    
    Available filters:
    - prefix: Exact prefix (e.g., "192.168.1.0/24")
    - site: Filter by site name (e.g., "SF1", "NYC1")
    - vrf: Filter by VRF name
    - tenant: Filter by tenant name
    - status: Filter by status (e.g., "active", "reserved", "deprecated")
    - role: Filter by prefix role
    - family: IP family (4 for IPv4, 6 for IPv6)
    - vlan: Filter by VLAN ID or name
    - is_pool: Filter for prefix pools (true/false)
    - search: Cross-field search across prefix, description, VLAN, and site
      IMPORTANT: Treats multiple words as AND (all must match). Use separate calls for OR logic.
    - limit: Maximum number of results (default 50, max 1000)
    
    Search strategy recommendations:
    - For multiple sites: Use separate calls rather than "SF1 NYC1" search
    - For CIDR patterns: Use exact prefix filter or search with single terms
    - For general search: Use single terms for best results
    
    Args:
        filter_params: Parameters to filter prefixes by (prefix, site, vrf, status, etc.)
        ctx: MCP context
    """
    from tools.prefixes import get_prefixes as get_prefixes_impl
    return get_prefixes_impl(filter_params, ctx)

@mcp.tool()
async def get_prefix_tool(prefix_id: int, ctx: Context) -> dict:
    """
    Get detailed information about a specific prefix by ID.
    
    Returns comprehensive information about a single prefix including
    utilization, available IPs, site assignment, and related details.
    
    Args:
        prefix_id: NetBox prefix ID
        ctx: MCP context
    """
    from tools.prefixes import get_prefix as get_prefix_impl
    return get_prefix_impl(prefix_id, ctx)

@mcp.tool()
async def ask_about_prefixes_tool(query: PrefixQuery, ctx: Context) -> dict:
    """
    Query prefixes using natural language.
    
    Examples:
        - "Show me all IPv4 prefixes at site SF1"
        - "List active prefixes in VRF production"
        - "Find all /24 subnets"
        - "Show reserved prefix pools"
        - "Get prefixes for tenant ABC"
    
    Args:
        query: Natural language query string
        ctx: MCP context
    """
    from tools.prefixes import ask_about_prefixes as ask_about_prefixes_impl
    return ask_about_prefixes_impl(query, ctx)

if __name__ == "__main__":
    mcp.run()