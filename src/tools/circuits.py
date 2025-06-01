"""
MCP tools for interacting with NetBox circuits.
"""

from typing import Dict, List, Optional, Union, Any
import re
from fastmcp import Context
from fastmcp.exceptions import ToolError

from config.netbox import get_netbox_client
from models.circuit import CircuitFilterParameters, CircuitQuery, CircuitSummary


def _parse_natural_language_query(query: str) -> CircuitFilterParameters:
    """
    Parse a natural language query into structured filter parameters.
    
    Args:
        query: Natural language query string
        
    Returns:
        CircuitFilterParameters object with appropriate filters set
    """
    params = CircuitFilterParameters()
    
    # Extract circuit ID
    cid_match = re.search(r'circuit (?:id|cid) ([A-Za-z0-9\-_]+)', query, re.IGNORECASE)
    if not cid_match:
        cid_match = re.search(r'cid ([A-Za-z0-9\-_]+)', query, re.IGNORECASE)
    if cid_match:
        params.cid = cid_match.group(1)
    
    # Extract provider information
    provider_match = re.search(r'provider (\w+)', query, re.IGNORECASE)
    if provider_match:
        params.provider = provider_match.group(1)
    
    # Extract circuit type information
    if re.search(r'internet', query, re.IGNORECASE):
        params.type = 'Internet'
    elif re.search(r'mpls', query, re.IGNORECASE):
        params.type = 'MPLS'
    elif re.search(r'point.to.point|p2p', query, re.IGNORECASE):
        params.type = 'Point-to-Point'
    elif re.search(r'ethernet', query, re.IGNORECASE):
        params.type = 'Ethernet'
    elif re.search(r'fiber', query, re.IGNORECASE):
        params.type = 'Fiber'
    
    # Extract site information
    site_match = re.search(r'(?:at|in|from|to) (?:site|location) (\w+)', query, re.IGNORECASE)
    if not site_match:
        site_match = re.search(r'(?:at|in|from|to) (\w+) (?:site|location)', query, re.IGNORECASE)
    if not site_match:
        site_match = re.search(r'site (\w+)', query, re.IGNORECASE)
    if site_match:
        params.site = site_match.group(1)
    
    # Extract status information
    if re.search(r'active', query, re.IGNORECASE):
        params.status = 'active'
    elif re.search(r'planned', query, re.IGNORECASE):
        params.status = 'planned'
    elif re.search(r'provisioning', query, re.IGNORECASE):
        params.status = 'provisioning'
    elif re.search(r'deprovisioning', query, re.IGNORECASE):
        params.status = 'deprovisioning'
    elif re.search(r'offline', query, re.IGNORECASE):
        params.status = 'offline'
    
    # Extract tenant information
    tenant_match = re.search(r'tenant (\w+)', query, re.IGNORECASE)
    if tenant_match:
        params.tenant = tenant_match.group(1)
        
    # Extract limit information
    limit_match = re.search(r'(?:limit|top|first) (\d+)', query, re.IGNORECASE)
    if limit_match:
        try:
            limit = int(limit_match.group(1))
            params.limit = min(max(limit, 1), 1000)  # Ensure between 1 and 1000
        except ValueError:
            pass
    
    return params


def _format_circuit_summary(circuit: Dict[str, Any], nb=None) -> CircuitSummary:
    """
    Convert a NetBox circuit dictionary to a CircuitSummary object.
    
    Args:
        circuit: Circuit data from NetBox API
        nb: NetBox client instance for additional queries
        
    Returns:
        CircuitSummary object with formatted circuit information
    """
    # Extract provider name
    provider_name = None
    if circuit.get('provider'):
        if isinstance(circuit['provider'], dict):
            provider_name = circuit['provider'].get('name', '')
        else:
            provider_name = getattr(circuit['provider'], 'name', '')
    
    # Extract circuit type name
    type_name = None
    if circuit.get('type'):
        if isinstance(circuit['type'], dict):
            type_name = circuit['type'].get('name', '')
        else:
            type_name = getattr(circuit['type'], 'name', '')
    
    # Extract status
    status = None
    if circuit.get('status'):
        if isinstance(circuit['status'], dict):
            status = circuit['status'].get('value', '')
        else:
            status = getattr(circuit['status'], 'value', str(circuit['status']))
    
    # Extract tenant name
    tenant_name = None
    if circuit.get('tenant'):
        if isinstance(circuit['tenant'], dict):
            tenant_name = circuit['tenant'].get('name', '')
        else:
            tenant_name = getattr(circuit['tenant'], 'name', '')
    
    # Extract termination sites - need to fetch from circuit terminations API
    termination_a = None
    termination_z = None
    
    if nb and circuit.get('id'):
        try:
            # Get circuit terminations by circuit ID
            terminations = list(nb.circuits.circuit_terminations.filter(circuit_id=circuit['id']))
            for term in terminations:
                if hasattr(term, 'site') and term.site:
                    site_name = getattr(term.site, 'name', '')
                    term_side = getattr(term, 'term_side', '').upper()
                    if term_side == 'A':
                        termination_a = site_name
                    elif term_side == 'Z':
                        termination_z = site_name
        except Exception:
            # If we can't get terminations, continue without them
            pass
    
    # Extract tags
    tags = []
    if circuit.get('tags') and isinstance(circuit['tags'], list):
        for tag in circuit['tags']:
            if isinstance(tag, dict) and 'name' in tag:
                tags.append(tag['name'])
            elif hasattr(tag, 'name'):
                tags.append(tag.name)
            elif isinstance(tag, str):
                tags.append(tag)
    
    # Extract install date
    install_date = None
    if circuit.get('install_date'):
        install_date = str(circuit['install_date'])
    
    return CircuitSummary(
        id=circuit.get('id', 0),
        cid=circuit.get('cid', ''),
        provider=provider_name or '',
        type=type_name or '',
        status=status or '',
        description=circuit.get('description', ''),
        install_date=install_date,
        commit_rate=circuit.get('commit_rate'),
        tenant=tenant_name,
        termination_a=termination_a,
        termination_z=termination_z,
        tags=tags
    )


def get_circuits_by_filter(mcp, filter_params: CircuitFilterParameters, ctx: Context) -> List[CircuitSummary]:
    """
    Get circuits from NetBox based on filter parameters.
    
    Args:
        filter_params: Parameters to filter circuits by
        ctx: MCP context
        
    Returns:
        List of circuit summary objects
    """
    try:
        nb = get_netbox_client()
        
        # Convert filter params to dict and remove None values
        params = {k: v for k, v in filter_params.model_dump().items() if v is not None and k != 'limit'}
        limit = filter_params.limit
        site_filter = params.pop('site', None)  # Handle site filtering separately
        
        # Adapt parameters to match NetBox API requirements
        adapted_params = {}
        
        # Special handling for provider
        if 'provider' in params:
            provider_value = params.pop('provider')
            # Check if provider is a name or an ID
            if provider_value.isdigit():
                adapted_params['provider_id'] = provider_value
            else:
                # Try to find provider by name
                try:
                    provider = nb.circuits.providers.get(name=provider_value)
                    if provider:
                        adapted_params['provider_id'] = provider.id
                    else:
                        # Try case-insensitive search
                        providers = list(nb.circuits.providers.filter(name__ic=provider_value))
                        if providers:
                            adapted_params['provider_id'] = providers[0].id
                        else:
                            adapted_params['provider'] = provider_value
                except Exception:
                    adapted_params['provider'] = provider_value
        
        # Special handling for circuit type
        if 'type' in params:
            type_value = params.pop('type')
            # Try to find circuit type by name
            try:
                circuit_types = list(nb.circuits.circuit_types.filter(name__ic=type_value))
                if circuit_types:
                    adapted_params['type_id'] = circuit_types[0].id
                else:
                    adapted_params['type'] = type_value
            except Exception:
                adapted_params['type'] = type_value
        
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
        
        # Handle remaining parameters
        for key, value in params.items():
            if key not in ['limit', 'site']:
                adapted_params[key] = value
        
        # Query NetBox API with a higher limit to allow for post-filtering by site
        query_limit = limit * 3 if site_filter else limit
        circuits = nb.circuits.circuits.filter(**adapted_params, limit=query_limit)
        
        # Convert to CircuitSummary objects
        results = [_format_circuit_summary(dict(circuit), nb) for circuit in circuits]
        
        # Post-filter by site if specified
        if site_filter:
            site_filter_lower = site_filter.lower()
            filtered_results = []
            for circuit in results:
                # Check if circuit terminates at the specified site (either A or Z side)
                if (circuit.termination_a and circuit.termination_a.lower() == site_filter_lower) or \
                   (circuit.termination_z and circuit.termination_z.lower() == site_filter_lower):
                    filtered_results.append(circuit)
                    if len(filtered_results) >= limit:
                        break
            return filtered_results
        
        return results[:limit]
    
    except Exception as e:
        raise ToolError(f"Failed to get circuits: {str(e)}")


def get_circuit_by_cid(mcp, cid: str, ctx: Context) -> CircuitSummary:
    """
    Get a specific circuit by circuit ID.
    
    Args:
        cid: Circuit ID
        ctx: MCP context
        
    Returns:
        Circuit summary object
    """
    try:
        nb = get_netbox_client()
        
        # Try getting by CID
        circuit = nb.circuits.circuits.get(cid=cid)
                
        if not circuit:
            raise ToolError(f"Circuit with CID '{cid}' not found")
                
        return _format_circuit_summary(dict(circuit), nb)
            
    except Exception as e:
        raise ToolError(f"Failed to get circuit: {str(e)}")


def query_circuits(mcp, query: CircuitQuery, ctx: Context) -> List[CircuitSummary]:
    """
    Query circuits using natural language.
    
    Args:
        query: Natural language query
        ctx: MCP context
        
    Returns:
        List of matching circuit summary objects
    """
    try:
        # Parse the natural language query into filter parameters
        filter_params = _parse_natural_language_query(query.query)
        
        # Handle queries about specific circuits
        if any(pattern in query.query.lower() for pattern in ["about", "tell me about", "information on", "details for"]) and filter_params.cid:
            try:
                circuit = get_circuit_by_cid(mcp, filter_params.cid, ctx)
                return [circuit]
            except ToolError:
                # Fall back to filter search if exact match fails
                pass
        
        # Use the parsed parameters to filter circuits
        return get_circuits_by_filter(mcp, filter_params, ctx)
        
    except Exception as e:
        # Provide more helpful error messages
        error_msg = str(e)
        if "not one of the available choices" in error_msg:
            if "provider" in error_msg:
                return [CircuitSummary(
                    id=0,
                    cid="Error",
                    provider="",
                    type="",
                    status="",
                    description="The provider you specified doesn't match any available providers in NetBox. Check the provider name and try again."
                )]
            elif "type" in error_msg:
                return [CircuitSummary(
                    id=0,
                    cid="Error",
                    provider="",
                    type="",
                    status="",
                    description="The circuit type you specified doesn't match any available types in NetBox. Common types include 'Internet', 'MPLS', 'Point-to-Point'."
                )]
        
        raise ToolError(f"Failed to query circuits: {str(e)}")