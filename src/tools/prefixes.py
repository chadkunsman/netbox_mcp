"""
MCP tools for interacting with NetBox prefixes.
"""

from typing import Dict, List, Optional, Union, Any
import re
from fastmcp import Context
from fastmcp.exceptions import ToolError

from config.netbox import get_netbox_client
from models.prefix import PrefixFilterParameters, PrefixQuery, PrefixSummary


def _parse_natural_language_query(query: str) -> PrefixFilterParameters:
    """
    Parse a natural language query into structured filter parameters.
    
    Args:
        query: Natural language query string
        
    Returns:
        PrefixFilterParameters object with appropriate filters set
    """
    params = PrefixFilterParameters()
    
    # Extract site information (standardized)
    site_match = re.search(r'(?:at|in|from)\s+(?:site\s+)?(\w+)', query, re.IGNORECASE)
    if site_match:
        params.site = site_match.group(1)
    
    # Extract IP family information (keep domain-specific intelligence)
    if re.search(r'ipv4|ip4|v4', query, re.IGNORECASE):
        params.family = 4
    elif re.search(r'ipv6|ip6|v6', query, re.IGNORECASE):
        params.family = 6
    
    # Extract status information (keep limited valid values)
    if re.search(r'active', query, re.IGNORECASE):
        params.status = 'active'
    elif re.search(r'reserved', query, re.IGNORECASE):
        params.status = 'reserved'
    elif re.search(r'deprecated', query, re.IGNORECASE):
        params.status = 'deprecated'
    elif re.search(r'container', query, re.IGNORECASE):
        params.status = 'container'
    
    # Extract pool information
    if re.search(r'pool', query, re.IGNORECASE):
        params.is_pool = True
    
    # Extract prefix pattern (CIDR notation - genuinely useful)
    prefix_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', query)
    if not prefix_match:
        # Try IPv6 pattern
        prefix_match = re.search(r'([0-9a-fA-F:]+/\d{1,3})', query)
    if prefix_match:
        params.prefix = prefix_match.group(1)
    
    # Extract VRF information
    vrf_match = re.search(r'vrf\s+(\w+)', query, re.IGNORECASE)
    if vrf_match:
        params.vrf = vrf_match.group(1)
    
    # Extract VLAN information (simplified)
    vlan_match = re.search(r'(?:vlan|vid)\s*(\w+)', query, re.IGNORECASE)
    if vlan_match:
        params.vlan = vlan_match.group(1)
    
    # Extract limit information
    limit_match = re.search(r'(?:first|top|limit)\s+(\d+)', query, re.IGNORECASE)
    if limit_match:
        params.limit = min(int(limit_match.group(1)), 1000)
    
    # If no specific filters found, use general search
    if not any([params.site, params.family, params.status, params.prefix, params.vrf, params.vlan, params.is_pool]):
        params.search = query
    
    return params


def _format_prefix_for_display(prefix_data: Dict[str, Any]) -> PrefixSummary:
    """
    Convert NetBox prefix data into a formatted summary.
    
    Args:
        prefix_data: Raw prefix data from NetBox API
        
    Returns:
        PrefixSummary object with formatted data
    """
    # Extract nested object names safely
    site_name = None
    if prefix_data.get('site'):
        site_name = prefix_data['site'].get('name') if isinstance(prefix_data['site'], dict) else str(prefix_data['site'])
    
    vrf_name = None
    if prefix_data.get('vrf'):
        vrf_name = prefix_data['vrf'].get('name') if isinstance(prefix_data['vrf'], dict) else str(prefix_data['vrf'])
    
    tenant_name = None
    if prefix_data.get('tenant'):
        tenant_name = prefix_data['tenant'].get('name') if isinstance(prefix_data['tenant'], dict) else str(prefix_data['tenant'])
    
    vlan_name = None
    if prefix_data.get('vlan'):
        if isinstance(prefix_data['vlan'], dict):
            # VLAN object with name and vid
            vlan_name = prefix_data['vlan'].get('name', '')
            vlan_vid = prefix_data['vlan'].get('vid', '')
            if vlan_name and vlan_vid:
                vlan_name = f"{vlan_name} (VID {vlan_vid})"
            elif vlan_vid:
                vlan_name = f"VLAN {vlan_vid}"
        else:
            vlan_name = str(prefix_data['vlan'])
    
    role_name = None
    if prefix_data.get('role'):
        role_name = prefix_data['role'].get('name') if isinstance(prefix_data['role'], dict) else str(prefix_data['role'])
    
    # Handle status
    status = 'unknown'
    if prefix_data.get('status'):
        if isinstance(prefix_data['status'], dict):
            status = prefix_data['status'].get('label', prefix_data['status'].get('value', 'unknown'))
        else:
            status = str(prefix_data['status'])
    
    # Handle family
    family = 'IPv4'
    if prefix_data.get('family'):
        if isinstance(prefix_data['family'], dict):
            family_value = prefix_data['family'].get('value', 4)
            family = 'IPv6' if family_value == 6 else 'IPv4'
        elif isinstance(prefix_data['family'], int):
            family = 'IPv6' if prefix_data['family'] == 6 else 'IPv4'
    
    # Extract tags
    tags = []
    if prefix_data.get('tags'):
        if isinstance(prefix_data['tags'], list):
            for tag in prefix_data['tags']:
                if isinstance(tag, dict):
                    tags.append(tag.get('name', str(tag)))
                else:
                    tags.append(str(tag))
    
    return PrefixSummary(
        id=prefix_data.get('id', 0),
        prefix=prefix_data.get('prefix', ''),
        site=site_name,
        vrf=vrf_name,
        tenant=tenant_name,
        vlan=vlan_name,
        status=status,
        role=role_name,
        family=family,
        is_pool=prefix_data.get('is_pool', False),
        description=prefix_data.get('description', ''),
        tags=tags,
        utilization=prefix_data.get('utilization'),
        available_ips=prefix_data.get('available_ips'),
        created=prefix_data.get('created'),
        last_updated=prefix_data.get('last_updated')
    )


def get_prefixes(filter_params: PrefixFilterParameters, ctx: Context) -> Dict[str, Any]:
    """
    Retrieve prefixes from NetBox with filtering options.
    
    Args:
        filter_params: Filter parameters for prefix search
        ctx: FastMCP context
        
    Returns:
        Dictionary containing prefixes and metadata
        
    Raises:
        ToolError: If the request fails or no prefixes are found
    """
    try:
        nb = get_netbox_client()
        
        # Build query parameters
        query_params = {}
        
        # Handle cross-field search
        if filter_params.search:
            query_params['q'] = filter_params.search  # NetBox's general search parameter
        
        if filter_params.prefix:
            query_params['prefix'] = filter_params.prefix
        
        # Special handling for site (similar to devices tool)
        if filter_params.site:
            site_value = filter_params.site
            if site_value.isdigit():
                query_params['site_id'] = site_value
            else:
                # Try to find site by name
                try:
                    site = nb.dcim.sites.get(name=site_value)
                    if site:
                        query_params['site_id'] = site.id
                    else:
                        # Try case-insensitive search
                        sites = list(nb.dcim.sites.filter(name__ic=site_value))
                        if sites:
                            query_params['site_id'] = sites[0].id
                        else:
                            raise ToolError(f"Site '{site_value}' not found. Please check the site name.")
                except Exception as e:
                    if "not found" in str(e):
                        raise e
                    raise ToolError(f"Error looking up site '{site_value}': {str(e)}")
        
        if filter_params.vrf:
            query_params['vrf'] = filter_params.vrf
        if filter_params.tenant:
            query_params['tenant'] = filter_params.tenant
        
        # Special handling for VLAN (similar to site)
        if filter_params.vlan:
            vlan_value = filter_params.vlan
            if vlan_value.isdigit():
                # Could be VLAN ID or VID
                try:
                    vlan = nb.ipam.vlans.get(id=vlan_value)
                    if vlan:
                        query_params['vlan_id'] = vlan.id
                    else:
                        # Try by VID
                        vlan = nb.ipam.vlans.get(vid=vlan_value)
                        if vlan:
                            query_params['vlan_id'] = vlan.id
                        else:
                            raise ToolError(f"VLAN with ID or VID '{vlan_value}' not found.")
                except Exception as e:
                    if "not found" in str(e):
                        raise e
                    raise ToolError(f"Error looking up VLAN '{vlan_value}': {str(e)}")
            else:
                # Try to find VLAN by name
                try:
                    vlan = nb.ipam.vlans.get(name=vlan_value)
                    if vlan:
                        query_params['vlan_id'] = vlan.id
                    else:
                        # Try case-insensitive search
                        vlans = list(nb.ipam.vlans.filter(name__ic=vlan_value))
                        if vlans:
                            query_params['vlan_id'] = vlans[0].id
                        else:
                            raise ToolError(f"VLAN '{vlan_value}' not found. Please check the VLAN name.")
                except Exception as e:
                    if "not found" in str(e):
                        raise e
                    raise ToolError(f"Error looking up VLAN '{vlan_value}': {str(e)}")
        if filter_params.status:
            query_params['status'] = filter_params.status
        if filter_params.role:
            query_params['role'] = filter_params.role
        if filter_params.family:
            query_params['family'] = filter_params.family
        if filter_params.is_pool is not None:
            query_params['is_pool'] = filter_params.is_pool
        if filter_params.tag:
            query_params['tag'] = filter_params.tag
        
        query_params['limit'] = filter_params.limit
        
        # Execute query
        prefixes = list(nb.ipam.prefixes.filter(**query_params))
        
        if not prefixes:
            return {
                "message": "No prefixes found matching the specified criteria",
                "count": 0,
                "prefixes": []
            }
        
        # Format prefixes for display
        formatted_prefixes = []
        for prefix in prefixes:
            try:
                formatted_prefix = _format_prefix_for_display(dict(prefix))
                formatted_prefixes.append(formatted_prefix.model_dump())
            except Exception as e:
                # Log the error but continue processing other prefixes
                continue
        
        return {
            "message": f"Found {len(formatted_prefixes)} prefix(es)",
            "count": len(formatted_prefixes),
            "prefixes": formatted_prefixes
        }
        
    except Exception as e:
        raise ToolError(f"Failed to retrieve prefixes: {str(e)}")


def get_prefix(prefix_id: int, ctx: Context) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific prefix by ID.
    
    Args:
        prefix_id: NetBox prefix ID
        ctx: FastMCP context
        
    Returns:
        Dictionary containing detailed prefix information
        
    Raises:
        ToolError: If the prefix is not found or request fails
    """
    try:
        nb = get_netbox_client()
        
        prefix = nb.ipam.prefixes.get(prefix_id)
        if not prefix:
            raise ToolError(f"Prefix with ID {prefix_id} not found")
        
        formatted_prefix = _format_prefix_for_display(dict(prefix))
        
        return {
            "message": f"Retrieved prefix details for {formatted_prefix.prefix}",
            "prefix": formatted_prefix.model_dump()
        }
        
    except Exception as e:
        raise ToolError(f"Failed to retrieve prefix {prefix_id}: {str(e)}")


def ask_about_prefixes(query: PrefixQuery, ctx: Context) -> Dict[str, Any]:
    """
    Process natural language queries about prefixes and return relevant results.
    
    Args:
        query: Natural language query about prefixes
        ctx: FastMCP context
        
    Returns:
        Dictionary containing query results and explanations
        
    Raises:
        ToolError: If the query cannot be processed or fails
    """
    try:
        # Parse the natural language query
        filter_params = _parse_natural_language_query(query.query)
        
        # Execute the search
        result = get_prefixes(filter_params, ctx)
        
        # Add query interpretation to the response
        interpretation = []
        if filter_params.prefix:
            interpretation.append(f"Prefix: {filter_params.prefix}")
        if filter_params.site:
            interpretation.append(f"Site: {filter_params.site}")
        if filter_params.family:
            family_str = "IPv6" if filter_params.family == 6 else "IPv4"
            interpretation.append(f"IP Family: {family_str}")
        if filter_params.status:
            interpretation.append(f"Status: {filter_params.status}")
        if filter_params.is_pool is not None:
            interpretation.append(f"Pool: {'Yes' if filter_params.is_pool else 'No'}")
        if filter_params.vrf:
            interpretation.append(f"VRF: {filter_params.vrf}")
        if filter_params.tenant:
            interpretation.append(f"Tenant: {filter_params.tenant}")
        if filter_params.vlan:
            interpretation.append(f"VLAN: {filter_params.vlan}")
        if filter_params.limit != 50:
            interpretation.append(f"Limit: {filter_params.limit}")
        
        result["query_interpretation"] = interpretation
        result["original_query"] = query.query
        
        return result
        
    except Exception as e:
        raise ToolError(f"Failed to process prefix query '{query.query}': {str(e)}")