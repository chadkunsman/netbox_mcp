"""
MCP tools for interacting with NetBox devices.
"""

from typing import Dict, List, Optional, Union, Any
import re
from fastmcp import Context
from fastmcp.exceptions import ToolError

from config.netbox import get_netbox_client
from models.device import DeviceFilterParameters, DeviceQuery, DeviceSummary


def _parse_natural_language_query(query: str) -> DeviceFilterParameters:
    """
    Parse a natural language query into structured filter parameters.
    
    Args:
        query: Natural language query string
        
    Returns:
        DeviceFilterParameters object with appropriate filters set
    """
    params = DeviceFilterParameters()
    
    # Extract site information
    site_match = re.search(r'(?:at|in|from) (?:site|location) (\w+)', query, re.IGNORECASE)
    if not site_match:
        site_match = re.search(r'(?:at|in|from) (\w+) (?:site|location)', query, re.IGNORECASE)
    if not site_match:
        site_match = re.search(r'site (\w+)', query, re.IGNORECASE)
    if site_match:
        params.site = site_match.group(1)
    
    # Extract role information
    if re.search(r'firewall', query, re.IGNORECASE):
        params.role = 'net-firewall'
    elif re.search(r'router', query, re.IGNORECASE):
        params.role = 'router'
    elif re.search(r'switch', query, re.IGNORECASE):
        params.role = 'office_access_switch'
    elif re.search(r'wireless|accesspoint|ap', query, re.IGNORECASE):
        params.role = 'net-wireless-accesspoint'
    elif re.search(r'server', query, re.IGNORECASE):
        params.role = 'server'
    
    # Extract status information
    if re.search(r'active', query, re.IGNORECASE):
        params.status = 'active'
    elif re.search(r'planned', query, re.IGNORECASE):
        params.status = 'planned'
    elif re.search(r'staged', query, re.IGNORECASE):
        params.status = 'staged'
    elif re.search(r'failed', query, re.IGNORECASE):
        params.status = 'failed'
    elif re.search(r'offline', query, re.IGNORECASE):
        params.status = 'offline'
    
    # Extract specific device name patterns
    name_match = re.search(r'device (\w+[\w\.-]*)', query, re.IGNORECASE)
    if not name_match:
        name_match = re.search(r'(\w+[\w\.-]*) device', query, re.IGNORECASE)
    if name_match:
        params.name = name_match.group(1)
    
    # If no specific filters found, use general search
    if not any([params.site, params.role, params.status, params.name]):
        params.search = query
    
    # Extract manufacturer information
    manufacturer_match = re.search(r'manufacturer (\w+)', query, re.IGNORECASE)
    if manufacturer_match:
        params.manufacturer = manufacturer_match.group(1)
        
    # Extract model information
    model_match = re.search(r'model (\w+[\w\.-]*)', query, re.IGNORECASE)
    if model_match:
        params.model = model_match.group(1)
        
    # Extract limit information
    limit_match = re.search(r'(?:limit|top|first) (\d+)', query, re.IGNORECASE)
    if limit_match:
        try:
            limit = int(limit_match.group(1))
            params.limit = min(max(limit, 1), 1000)  # Ensure between 1 and 1000
        except ValueError:
            pass
    
    return params


def _format_device_summary(device: Dict[str, Any]) -> DeviceSummary:
    """
    Convert a NetBox device dictionary to a DeviceSummary object.
    
    Args:
        device: Device data from NetBox API
        
    Returns:
        DeviceSummary object with formatted device information
    """
    # Extract primary IP if available
    ip_address = None
    if device.get('primary_ip'):
        ip_address = device['primary_ip'].get('address', '').split('/')[0]  # Remove CIDR notation
    elif device.get('primary_ip4'):
        ip_address = device['primary_ip4'].get('address', '').split('/')[0]
    
    # Extract site name
    site_name = None
    if device.get('site'):
        if isinstance(device['site'], dict):
            site_name = device['site'].get('name', '')
        else:
            # Handle if site is an object with attributes
            site_name = getattr(device['site'], 'name', '')
    
    # Extract role name
    role_name = None
    if device.get('device_role'):
        if isinstance(device['device_role'], dict):
            role_name = device['device_role'].get('name', '')
        else:
            # Handle if role is an object with attributes
            role_name = getattr(device['device_role'], 'name', '')
    
    # Extract model name
    model_name = None
    if device.get('device_type'):
        if isinstance(device['device_type'], dict):
            model_name = device['device_type'].get('model', '')
        else:
            # Handle if device_type is an object with attributes
            model_name = getattr(device['device_type'], 'model', '')
    
    # Extract status
    status = None
    if device.get('status'):
        if isinstance(device['status'], dict):
            status = device['status'].get('value', '')
        else:
            # Handle if status is an object or string
            status = getattr(device['status'], 'value', str(device['status']))
    
    # Extract tags
    tags = []
    if device.get('tags') and isinstance(device['tags'], list):
        for tag in device['tags']:
            if isinstance(tag, dict) and 'name' in tag:
                tags.append(tag['name'])
            elif hasattr(tag, 'name'):
                tags.append(tag.name)
            elif isinstance(tag, str):
                tags.append(tag)
    
    return DeviceSummary(
        id=device.get('id', 0),
        name=device.get('name', ''),
        site=site_name or '',
        role=role_name or '',
        status=status or '',
        model=model_name or '',
        ip_address=ip_address,
        serial=device.get('serial', ''),
        description=device.get('description', ''),
        tags=tags
    )


def get_devices_by_filter(mcp, filter_params: DeviceFilterParameters, ctx: Context) -> List[DeviceSummary]:
    """
    Get devices from NetBox based on filter parameters.
    
    Args:
        filter_params: Parameters to filter devices by
        ctx: MCP context
        
    Returns:
        List of device summary objects
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
                            # If no matches, include the original value (it will likely fail but with a clearer error)
                            adapted_params['site'] = site_value
                except Exception:
                    # If lookup fails, use the name as-is
                    adapted_params['site'] = site_value
        
        # Special handling for role
        if 'role' in params:
            role_value = params.pop('role')
            # Try to find device role by name
            try:
                roles = list(nb.dcim.device_roles.filter(name__ic=role_value))
                if roles:
                    adapted_params['role_id'] = roles[0].id
                else:
                    # If no matches, include the original value
                    adapted_params['role'] = role_value
            except Exception:
                # If lookup fails, use the name as-is
                adapted_params['role'] = role_value
        
        # Special handling for model/device_type
        if 'model' in params:
            model = params.pop('model')
            # Try to find device type by model name
            try:
                device_types = list(nb.dcim.device_types.filter(model__ic=model))
                if device_types:
                    adapted_params['device_type_id'] = device_types[0].id
                else:
                    adapted_params['device_type'] = model
            except Exception:
                # If lookup fails, use the name as-is
                adapted_params['device_type'] = model
        
        # Handle remaining parameters
        for key, value in params.items():
            if key not in ['limit']:
                adapted_params[key] = value
        
        # Query NetBox API
        devices = nb.dcim.devices.filter(**adapted_params, limit=limit)
        
        # Convert to DeviceSummary objects
        return [_format_device_summary(dict(device)) for device in devices]
    
    except Exception as e:
        raise ToolError(f"Failed to get devices: {str(e)}")


def get_device_by_name(mcp, name: str, ctx: Context) -> DeviceSummary:
    """
    Get a specific device by name.
    
    Args:
        name: Device name
        ctx: MCP context
        
    Returns:
        Device summary object
    """
    try:
        nb = get_netbox_client()
        
        # Try getting by name
        device = nb.dcim.devices.get(name=name)
                
        if not device:
            raise ToolError(f"Device with name '{name}' not found")
                
        return _format_device_summary(dict(device))
            
    except Exception as e:
        raise ToolError(f"Failed to get device: {str(e)}")


def query_devices(mcp, query: DeviceQuery, ctx: Context) -> List[DeviceSummary]:
    """
    Query devices using natural language.
    
    Args:
        query: Natural language query
        ctx: MCP context
        
    Returns:
        List of matching device summary objects
    """
    try:
        # Parse the natural language query into filter parameters
        filter_params = _parse_natural_language_query(query.query)
        
        # Handles queries about specific devices
        if any(pattern in query.query.lower() for pattern in ["about", "tell me about", "information on", "details for"]) and filter_params.name:
            try:
                device = get_device_by_name(mcp, filter_params.name, ctx)
                return [device]
            except ToolError:
                # Fall back to filter search if exact match fails
                pass
        
        # For site-specific queries, first verify if the site exists using a direct lookup
        nb = get_netbox_client()
        if filter_params.site:
            try:
                # Look for exact match first
                site = nb.dcim.sites.get(name=filter_params.site)
                if not site:
                    # Try case-insensitive search
                    sites = list(nb.dcim.sites.filter(name__ic=filter_params.site))
                    if sites:
                        filter_params.site = sites[0].name  # Use the exact site name
            except Exception:
                # If we can't find the site, continue with the user's input
                pass
        
        # Use the parsed parameters to filter devices
        return get_devices_by_filter(mcp, filter_params, ctx)
        
    except Exception as e:
        # Provide more helpful error messages
        error_msg = str(e)
        if "not one of the available choices" in error_msg:
            if "role" in error_msg:
                return [DeviceSummary(
                    id=0,
                    name="Error",
                    site="",
                    role="",
                    status="",
                    model="",
                    description="The device role you specified doesn't match any available roles in NetBox. Try using more generic terms like 'switch' or 'access point'."
                )]
            elif "site" in error_msg:
                return [DeviceSummary(
                    id=0,
                    name="Error",
                    site="",
                    role="",
                    status="",
                    model="",
                    description="The site you specified doesn't exist in NetBox. Available sites include SF1, NYC1, DEN1, etc."
                )]
        
        raise ToolError(f"Failed to query devices: {str(e)}")