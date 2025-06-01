"""
Pydantic models for prefix-related operations.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class PrefixFilterParameters(BaseModel):
    """Query parameters for filtering prefixes."""
    prefix: Optional[str] = Field(None, description="IP prefix (e.g., '192.168.1.0/24', '10.0.0.0/8')")
    search: Optional[str] = Field(None, description="Cross-field search across prefix, description, VLAN, and site")
    site: Optional[str] = Field(None, description="Site name or ID (e.g., 'SF1', 'NYC1', 'DEN1')")
    vrf: Optional[str] = Field(None, description="VRF name or ID")
    tenant: Optional[str] = Field(None, description="Tenant name or ID")
    vlan: Optional[str] = Field(None, description="VLAN name, ID, or VID (e.g., 'VLAN100', '25', '100')")
    status: Optional[str] = Field(None, description="Prefix status (e.g., 'active', 'reserved', 'deprecated')")
    role: Optional[str] = Field(None, description="Prefix role")
    family: Optional[int] = Field(None, description="IP family (4 for IPv4, 6 for IPv6)")
    is_pool: Optional[bool] = Field(None, description="Whether the prefix is a pool")
    tag: Optional[str] = Field(None, description="Tag name")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")


class PrefixQuery(BaseModel):
    """Natural language query structure for prefixes."""
    query: str = Field(..., min_length=3, description="Natural language query about prefixes")


class PrefixSummary(BaseModel):
    """Simplified prefix information model."""
    id: int
    prefix: str
    site: Optional[str] = None
    vrf: Optional[str] = None
    tenant: Optional[str] = None
    vlan: Optional[str] = None
    status: str
    role: Optional[str] = None
    family: str  # IPv4 or IPv6
    is_pool: bool
    description: Optional[str] = None
    tags: List[str] = []
    utilization: Optional[float] = None
    available_ips: Optional[int] = None
    created: Optional[str] = None
    last_updated: Optional[str] = None