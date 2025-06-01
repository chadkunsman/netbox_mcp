"""
MCP tools for interacting with NetBox sites.
"""

from typing import Dict, List, Optional, Union, Any
from fastmcp import Context
from fastmcp.exceptions import ToolError

from config.netbox import get_netbox_client
from models.site import SiteSummary, SiteBasic


def get_site_info_by_name(mcp, name: str, ctx: Context) -> SiteSummary:
    """
    Get comprehensive information about a site including devices and racks count.
    
    Args:
        mcp: FastMCP instance (unused but required for consistency)
        name: Site name
        ctx: MCP context
        
    Returns:
        Site summary information
    """
    try:
        nb = get_netbox_client()
        
        # Get site by name
        site = nb.dcim.sites.get(name=name)
        
        if not site:
            raise ToolError(f"Site with name '{name}' not found")
        
        # Extract basic site information
        site_dict = dict(site)
        
        # Extract region name if available
        region_name = None
        if site_dict.get('region'):
            if isinstance(site_dict['region'], dict):
                region_name = site_dict['region'].get('name', '')
            else:
                region_name = getattr(site_dict['region'], 'name', '')
        
        # Extract tenant name if available
        tenant_name = None
        if site_dict.get('tenant'):
            if isinstance(site_dict['tenant'], dict):
                tenant_name = site_dict['tenant'].get('name', '')
            else:
                tenant_name = getattr(site_dict['tenant'], 'name', '')
        
        # Extract status
        status = None
        if site_dict.get('status'):
            if isinstance(site_dict['status'], dict):
                status = site_dict['status'].get('value', '')
            else:
                status = getattr(site_dict['status'], 'value', str(site_dict['status']))
        
        # Extract tags
        tags = []
        if site_dict.get('tags') and isinstance(site_dict['tags'], list):
            for tag in site_dict['tags']:
                if isinstance(tag, dict) and 'name' in tag:
                    tags.append(tag['name'])
                elif hasattr(tag, 'name'):
                    tags.append(tag.name)
                elif isinstance(tag, str):
                    tags.append(tag)
        
        # Count devices at site
        device_count = len(list(nb.dcim.devices.filter(site_id=site.id)))
        
        # Count racks at site
        rack_count = len(list(nb.dcim.racks.filter(site_id=site.id)))
        
        return SiteSummary(
            id=site_dict.get('id', 0),
            name=site_dict.get('name', ''),
            slug=site_dict.get('slug', ''),
            status=status or '',
            region=region_name,
            tenant=tenant_name,
            facility=site_dict.get('facility', ''),
            asn=site_dict.get('asn'),
            time_zone=site_dict.get('time_zone', ''),
            description=site_dict.get('description', ''),
            physical_address=site_dict.get('physical_address', ''),
            shipping_address=site_dict.get('shipping_address', ''),
            latitude=site_dict.get('latitude'),
            longitude=site_dict.get('longitude'),
            tags=tags,
            device_count=device_count,
            rack_count=rack_count
        )
    
    except Exception as e:
        raise ToolError(f"Failed to get site info: {str(e)}")


def list_all_sites(mcp, limit: int = 50, ctx: Context = None) -> List[SiteBasic]:
    """
    List all sites with basic information.
    
    Args:
        mcp: FastMCP instance (unused but required for consistency)
        limit: Maximum number of sites to return (default 50)
        ctx: MCP context
        
    Returns:
        List of basic site information
    """
    try:
        nb = get_netbox_client()
        
        # Get all sites with limit
        sites = nb.dcim.sites.filter(limit=limit)
        
        result = []
        for site in sites:
            site_dict = dict(site)
            
            # Extract region name if available
            region_name = None
            if site_dict.get('region'):
                if isinstance(site_dict['region'], dict):
                    region_name = site_dict['region'].get('name', '')
                else:
                    region_name = getattr(site_dict['region'], 'name', '')
            
            # Extract status
            status = None
            if site_dict.get('status'):
                if isinstance(site_dict['status'], dict):
                    status = site_dict['status'].get('value', '')
                else:
                    status = getattr(site_dict['status'], 'value', str(site_dict['status']))
            
            result.append(SiteBasic(
                id=site_dict.get('id', 0),
                name=site_dict.get('name', ''),
                slug=site_dict.get('slug', ''),
                status=status or '',
                region=region_name,
                description=site_dict.get('description', '')
            ))
        
        return result
    
    except Exception as e:
        raise ToolError(f"Failed to list sites: {str(e)}")