"""
NetBox MCP Server

A read-only FastMCP server that provides tools for interacting with NetBox API
with a focus on device-related operations. This server only allows querying 
information from NetBox without making any modifications to the data.
"""

import os
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError

from models.device import DeviceFilterParameters, DeviceQuery, DeviceSummary
from models.site import SiteSummary, SiteBasic
from models.circuit import CircuitFilterParameters, CircuitQuery, CircuitSummary
from tools.devices import get_devices_by_filter, get_device_by_name, query_devices
from tools.sites import get_site_info_by_name, list_all_sites
from tools.circuits import get_circuits_by_filter, get_circuit_by_cid, query_circuits

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("NetBox Device MCP Server")

# Register tools
@mcp.tool()
async def get_devices(filter_params: DeviceFilterParameters, ctx: Context) -> list[DeviceSummary]:
    """
    Get devices from NetBox based on filter parameters.
    
    Allows filtering devices by name, site, role, status, and other parameters.
    Returns a list of device objects with key information.
    
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
    
    Allows filtering circuits by CID, provider, type, status, and other parameters.
    Returns a list of circuit objects with key information including termination sites.
    
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

if __name__ == "__main__":
    mcp.run()