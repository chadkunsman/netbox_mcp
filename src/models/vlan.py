"""
Pydantic models for NetBox VLAN operations.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class VlanFilterParameters(BaseModel):
    """Parameters for filtering VLANs from NetBox."""
    
    vid: Optional[int] = Field(None, description="VLAN ID number (e.g., 100)")
    name: Optional[str] = Field(None, description="Exact VLAN name")
    name_contains: Optional[str] = Field(None, description="Substring search in VLAN name (case-insensitive)")
    site: Optional[str] = Field(None, description="Site name or ID")
    group: Optional[str] = Field(None, description="VLAN group name")
    tenant: Optional[str] = Field(None, description="Tenant name")
    role: Optional[str] = Field(None, description="VLAN role")
    status: Optional[str] = Field(None, description="Status (active, reserved, deprecated)")
    search: Optional[str] = Field(None, description="Cross-field search across name, description, and VID")
    description_contains: Optional[str] = Field(None, description="Substring search in VLAN description")
    tag: Optional[str] = Field(None, description="Filter by tag")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")


class VlanQuery(BaseModel):
    """Natural language query for VLANs."""
    
    query: str = Field(..., description="Natural language query about VLANs")


class VlanSummary(BaseModel):
    """Summary information for a VLAN."""
    
    id: int = Field(..., description="NetBox VLAN ID")
    vid: int = Field(..., description="VLAN ID number")
    name: str = Field(..., description="VLAN name")
    site: Optional[str] = Field(None, description="Site name")
    group: Optional[str] = Field(None, description="VLAN group name")
    tenant: Optional[str] = Field(None, description="Tenant name")
    role: Optional[str] = Field(None, description="VLAN role")
    status: str = Field(..., description="VLAN status")
    description: Optional[str] = Field(None, description="VLAN description")
    tags: List[str] = Field(default_factory=list, description="VLAN tags")
    created: Optional[str] = Field(None, description="Creation date")
    last_updated: Optional[str] = Field(None, description="Last updated date")