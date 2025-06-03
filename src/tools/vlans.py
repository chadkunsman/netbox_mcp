"""
MCP tools for interacting with NetBox VLANs.
"""

from typing import Dict, List, Optional, Union, Any
import re
from fastmcp import Context
from fastmcp.exceptions import ToolError

from config.netbox import get_netbox_client
from models.vlan import VlanFilterParameters, VlanQuery, VlanSummary


def _parse_natural_language_query(query: str) -> VlanFilterParameters:
    """
    Parse a natural language query into structured filter parameters.
    
    Args:
        query: Natural language query string
        
    Returns:
        VlanFilterParameters object with appropriate filters set
    """
    params = VlanFilterParameters()
    
    # Extract VID information (VLAN ID numbers)
    vid_match = re.search(r'(?:vlan|vid)\s+(\d+)', query, re.IGNORECASE)
    if vid_match:
        try:
            params.vid = int(vid_match.group(1))
        except ValueError:
            pass
    
    # Extract site information (more specific patterns to avoid false matches)
    site_match = re.search(r'(?:at|in|from)\s+(?:site\s+)?([A-Z0-9]+\d+|[A-Z]{2,4}\d+)', query, re.IGNORECASE)
    if not site_match:
        site_match = re.search(r'site\s+(\w+)', query, re.IGNORECASE)
    if site_match:
        params.site = site_match.group(1)
    
    # Extract status information
    if re.search(r'active', query, re.IGNORECASE):
        params.status = 'active'
    elif re.search(r'reserved', query, re.IGNORECASE):
        params.status = 'reserved'
    elif re.search(r'deprecated', query, re.IGNORECASE):
        params.status = 'deprecated'
    
    # Extract tenant information
    tenant_match = re.search(r'tenant\s+(\w+)', query, re.IGNORECASE)
    if tenant_match:
        params.tenant = tenant_match.group(1)
    
    # Extract limit information
    limit_match = re.search(r'(?:limit|top|first)\s+(\d+)', query, re.IGNORECASE)
    if limit_match:
        try:
            limit = int(limit_match.group(1))
            params.limit = min(max(limit, 1), 1000)
        except ValueError:
            pass
    
    # If no specific filters found, use general search
    if not any([params.vid, params.site, params.status, params.tenant]):
        params.search = query
    
    return params


def _format_vlan_summary(vlan: Dict[str, Any]) -> VlanSummary:
    """
    Convert a NetBox VLAN dictionary to a VlanSummary object.
    
    Args:
        vlan: VLAN data from NetBox API
        
    Returns:
        VlanSummary object with formatted VLAN information
    """
    # Extract site name
    site_name = None
    if vlan.get('site'):
        if isinstance(vlan['site'], dict):
            site_name = vlan['site'].get('name', '')
        else:
            site_name = getattr(vlan['site'], 'name', '')
    
    # Extract group name
    group_name = None
    if vlan.get('group'):
        if isinstance(vlan['group'], dict):
            group_name = vlan['group'].get('name', '')
        else:
            group_name = getattr(vlan['group'], 'name', '')
    
    # Extract tenant name
    tenant_name = None
    if vlan.get('tenant'):
        if isinstance(vlan['tenant'], dict):
            tenant_name = vlan['tenant'].get('name', '')
        else:
            tenant_name = getattr(vlan['tenant'], 'name', '')
    
    # Extract role name
    role_name = None
    if vlan.get('role'):
        if isinstance(vlan['role'], dict):
            role_name = vlan['role'].get('name', '')
        else:
            role_name = getattr(vlan['role'], 'name', '')
    
    # Extract status
    status = 'unknown'
    if vlan.get('status'):
        if isinstance(vlan['status'], dict):
            status = vlan['status'].get('value', '')
        else:
            status = getattr(vlan['status'], 'value', str(vlan['status']))
    
    # Extract tags
    tags = []
    if vlan.get('tags') and isinstance(vlan['tags'], list):
        for tag in vlan['tags']:
            if isinstance(tag, dict) and 'name' in tag:
                tags.append(tag['name'])
            elif hasattr(tag, 'name'):
                tags.append(tag.name)
            elif isinstance(tag, str):
                tags.append(tag)
    
    return VlanSummary(
        id=vlan.get('id', 0),
        vid=vlan.get('vid', 0),
        name=vlan.get('name', ''),
        site=site_name,
        group=group_name,
        tenant=tenant_name,
        role=role_name,
        status=status or '',
        description=vlan.get('description', ''),
        tags=tags,
        created=vlan.get('created'),
        last_updated=vlan.get('last_updated')
    )


def get_vlans_by_filter(mcp, filter_params: VlanFilterParameters, ctx: Context) -> List[VlanSummary]:
    """
    Get VLANs from NetBox based on filter parameters.
    
    Args:
        filter_params: Parameters to filter VLANs by
        ctx: MCP context
        
    Returns:
        List of VLAN summary objects
    """
    try:
        nb = get_netbox_client()
        
        # Convert filter params to dict and remove None values
        params = {k: v for k, v in filter_params.model_dump().items() if v is not None and k != 'limit'}
        limit = filter_params.limit
        
        # Adapt parameters to match NetBox API requirements
        adapted_params = {}
        
        # Handle name_contains for pattern matching
        if 'name_contains' in params:
            name_pattern = params.pop('name_contains')
            adapted_params['name__ic'] = name_pattern  # Case-insensitive contains
        
        # Handle description_contains for pattern matching
        if 'description_contains' in params:
            desc_pattern = params.pop('description_contains')
            adapted_params['description__ic'] = desc_pattern
        
        # Handle cross-field search
        if 'search' in params:
            search_term = params.pop('search')
            adapted_params['q'] = search_term  # NetBox's general search parameter
        
        # Special handling for site
        if 'site' in params:
            site_value = params.pop('site')
            # Check if site is a name or an ID
            if site_value.isdigit():
                adapted_params['site_id'] = site_value
            else:
                # Try to find site by name
                try:
                    site = nb.dcim.sites.get(name=site_value)
                    if site:
                        adapted_params['site_id'] = site.id
                    else:
                        # Try case-insensitive search
                        sites = list(nb.dcim.sites.filter(name__ic=site_value))
                        if sites:
                            adapted_params['site_id'] = sites[0].id
                        else:
                            adapted_params['site'] = site_value
                except Exception:
                    adapted_params['site'] = site_value
        
        # Special handling for tenant
        if 'tenant' in params:
            tenant_value = params.pop('tenant')
            try:
                tenant = nb.tenancy.tenants.get(name=tenant_value)
                if tenant:
                    adapted_params['tenant_id'] = tenant.id
                else:
                    tenants = list(nb.tenancy.tenants.filter(name__ic=tenant_value))
                    if tenants:
                        adapted_params['tenant_id'] = tenants[0].id
                    else:
                        adapted_params['tenant'] = tenant_value
            except Exception:
                adapted_params['tenant'] = tenant_value
        
        # Special handling for group
        if 'group' in params:
            group_value = params.pop('group')
            try:
                group = nb.ipam.vlan_groups.get(name=group_value)
                if group:
                    adapted_params['group_id'] = group.id
                else:
                    groups = list(nb.ipam.vlan_groups.filter(name__ic=group_value))
                    if groups:
                        adapted_params['group_id'] = groups[0].id
                    else:
                        adapted_params['group'] = group_value
            except Exception:
                adapted_params['group'] = group_value
        
        # Special handling for role
        if 'role' in params:
            role_value = params.pop('role')
            try:
                role = nb.ipam.roles.get(name=role_value)
                if role:
                    adapted_params['role_id'] = role.id
                else:
                    roles = list(nb.ipam.roles.filter(name__ic=role_value))
                    if roles:
                        adapted_params['role_id'] = roles[0].id
                    else:
                        adapted_params['role'] = role_value
            except Exception:
                adapted_params['role'] = role_value
        
        # Handle remaining parameters
        for key, value in params.items():
            if key not in ['limit']:
                adapted_params[key] = value
        
        # Query NetBox API
        vlans = nb.ipam.vlans.filter(**adapted_params, limit=limit)
        
        # Convert to VlanSummary objects
        return [_format_vlan_summary(dict(vlan)) for vlan in vlans]
    
    except Exception as e:
        raise ToolError(f"Failed to get VLANs: {str(e)}")


def get_vlan_by_id(mcp, vlan_id: int, ctx: Context) -> VlanSummary:
    """
    Get a specific VLAN by ID.
    
    Args:
        vlan_id: VLAN ID
        ctx: MCP context
        
    Returns:
        VLAN summary object
    """
    try:
        nb = get_netbox_client()
        
        # Try getting by ID
        vlan = nb.ipam.vlans.get(vlan_id)
                
        if not vlan:
            raise ToolError(f"VLAN with ID '{vlan_id}' not found")
                
        return _format_vlan_summary(dict(vlan))
            
    except Exception as e:
        raise ToolError(f"Failed to get VLAN: {str(e)}")


def query_vlans(mcp, query: VlanQuery, ctx: Context) -> List[VlanSummary]:
    """
    Query VLANs using natural language.
    
    Args:
        query: Natural language query
        ctx: MCP context
        
    Returns:
        List of matching VLAN summary objects
    """
    try:
        # Parse the natural language query into filter parameters
        filter_params = _parse_natural_language_query(query.query)
        
        # Handle queries about specific VLANs by ID
        if any(pattern in query.query.lower() for pattern in ["about", "tell me about", "information on", "details for"]) and filter_params.vid:
            try:
                # Try to find VLAN by VID first
                nb = get_netbox_client()
                vlan = nb.ipam.vlans.get(vid=filter_params.vid)
                if vlan:
                    return [_format_vlan_summary(dict(vlan))]
            except Exception:
                # Fall back to filter search if exact match fails
                pass
        
        # Use the parsed parameters to filter VLANs
        return get_vlans_by_filter(mcp, filter_params, ctx)
        
    except Exception as e:
        # Provide more helpful error messages
        error_msg = str(e)
        if "not one of the available choices" in error_msg:
            if "status" in error_msg:
                return [VlanSummary(
                    id=0,
                    vid=0,
                    name="Error",
                    site="",
                    status="",
                    description="The status you specified doesn't match any available statuses in NetBox. Try using 'active', 'reserved', or 'deprecated'."
                )]
        
        raise ToolError(f"Failed to query VLANs: {str(e)}")