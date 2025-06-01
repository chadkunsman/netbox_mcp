"""
Pydantic models for site-related operations.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SiteFilter(BaseModel):
    """Filter parameters for querying sites."""
    name: Optional[str] = Field(None, description="Site name (supports regex)")
    status: Optional[str] = Field(None, description="Site status (active, planned, etc.)")
    region: Optional[str] = Field(None, description="Region name or ID")
    tag: Optional[str] = Field(None, description="Tag name")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")


class SiteCreate(BaseModel):
    """Data for creating a new site."""
    name: str = Field(..., min_length=1, description="Site name")
    slug: Optional[str] = Field(None, description="Unique site slug")
    status: str = Field("active", description="Site status")
    region: Optional[str] = Field(None, description="Region ID or name")
    tenant: Optional[str] = Field(None, description="Tenant ID or name")
    facility: Optional[str] = Field(None, description="Facility name")
    asn: Optional[int] = Field(None, description="Autonomous System Number")
    time_zone: Optional[str] = Field(None, description="Time zone")
    description: Optional[str] = Field(None, description="Site description")
    physical_address: Optional[str] = Field(None, description="Physical address")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    latitude: Optional[float] = Field(None, description="GPS latitude coordinate")
    longitude: Optional[float] = Field(None, description="GPS longitude coordinate")
    tags: Optional[List[str]] = Field(None, description="List of tag names")
    custom_fields: Optional[Dict] = Field(None, description="Custom fields")


class SiteUpdate(BaseModel):
    """Data for updating an existing site."""
    name: Optional[str] = Field(None, min_length=1, description="Site name")
    slug: Optional[str] = Field(None, description="Unique site slug")
    status: Optional[str] = Field(None, description="Site status")
    region: Optional[str] = Field(None, description="Region ID or name")
    tenant: Optional[str] = Field(None, description="Tenant ID or name")
    facility: Optional[str] = Field(None, description="Facility name")
    asn: Optional[int] = Field(None, description="Autonomous System Number")
    time_zone: Optional[str] = Field(None, description="Time zone")
    description: Optional[str] = Field(None, description="Site description")
    physical_address: Optional[str] = Field(None, description="Physical address")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    latitude: Optional[float] = Field(None, description="GPS latitude coordinate")
    longitude: Optional[float] = Field(None, description="GPS longitude coordinate")
    tags: Optional[List[str]] = Field(None, description="List of tag names")
    custom_fields: Optional[Dict] = Field(None, description="Custom fields")


class SiteBasic(BaseModel):
    """Basic site information for listing."""
    id: int = Field(..., description="Site ID")
    name: str = Field(..., description="Site name")
    slug: str = Field(..., description="Site slug")
    status: str = Field(..., description="Site status")
    region: Optional[str] = Field(None, description="Region name")
    description: Optional[str] = Field(None, description="Site description")


class SiteSummary(BaseModel):
    """Summary information about a site."""
    id: int = Field(..., description="Site ID")
    name: str = Field(..., description="Site name")
    slug: str = Field(..., description="Site slug")
    status: str = Field(..., description="Site status")
    region: Optional[str] = Field(None, description="Region name")
    tenant: Optional[str] = Field(None, description="Tenant name")
    facility: Optional[str] = Field(None, description="Facility name")
    asn: Optional[int] = Field(None, description="Autonomous System Number")
    time_zone: Optional[str] = Field(None, description="Time zone")
    description: Optional[str] = Field(None, description="Site description")
    physical_address: Optional[str] = Field(None, description="Physical address")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    latitude: Optional[float] = Field(None, description="GPS latitude coordinate")
    longitude: Optional[float] = Field(None, description="GPS longitude coordinate")
    tags: List[str] = Field(default_factory=list, description="List of tag names")
    device_count: Optional[int] = Field(None, description="Number of devices at this site")
    rack_count: Optional[int] = Field(None, description="Number of racks at this site")