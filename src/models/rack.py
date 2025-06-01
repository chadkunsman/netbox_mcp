"""
Pydantic models for rack-related operations.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class RackFilter(BaseModel):
    """Filter parameters for querying racks."""
    name: Optional[str] = Field(None, description="Rack name (supports regex)")
    site: Optional[str] = Field(None, description="Site name or ID")
    status: Optional[str] = Field(None, description="Rack status (active, planned, etc.)")
    role: Optional[str] = Field(None, description="Rack role name or ID")
    tag: Optional[str] = Field(None, description="Tag name")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")


class RackCreate(BaseModel):
    """Data for creating a new rack."""
    name: str = Field(..., min_length=1, description="Rack name")
    site: Union[int, str] = Field(..., description="Site ID or name")
    status: str = Field("active", description="Rack status")
    role: Optional[Union[int, str]] = Field(None, description="Rack role ID or name")
    tenant: Optional[Union[int, str]] = Field(None, description="Tenant ID or name")
    serial: Optional[str] = Field(None, description="Serial number")
    asset_tag: Optional[str] = Field(None, description="Asset tag")
    type: Optional[str] = Field(None, description="Rack type")
    width: int = Field(19, description="Rack width in inches")
    u_height: int = Field(42, ge=1, le=100, description="Rack height in rack units")
    desc_units: bool = Field(False, description="Whether rack units are descending")
    outer_width: Optional[int] = Field(None, description="Outer width in millimeters")
    outer_depth: Optional[int] = Field(None, description="Outer depth in millimeters")
    outer_unit: Optional[str] = Field(None, description="Outer dimension unit (mm/in)")
    tags: Optional[List[str]] = Field(None, description="List of tag names")
    custom_fields: Optional[Dict] = Field(None, description="Custom fields")


class RackUpdate(BaseModel):
    """Data for updating an existing rack."""
    name: Optional[str] = Field(None, min_length=1, description="Rack name")
    site: Optional[Union[int, str]] = Field(None, description="Site ID or name")
    status: Optional[str] = Field(None, description="Rack status")
    role: Optional[Union[int, str]] = Field(None, description="Rack role ID or name")
    tenant: Optional[Union[int, str]] = Field(None, description="Tenant ID or name")
    serial: Optional[str] = Field(None, description="Serial number")
    asset_tag: Optional[str] = Field(None, description="Asset tag")
    type: Optional[str] = Field(None, description="Rack type")
    width: Optional[int] = Field(None, description="Rack width in inches")
    u_height: Optional[int] = Field(None, ge=1, le=100, description="Rack height in rack units")
    desc_units: Optional[bool] = Field(None, description="Whether rack units are descending")
    outer_width: Optional[int] = Field(None, description="Outer width in millimeters")
    outer_depth: Optional[int] = Field(None, description="Outer depth in millimeters")
    outer_unit: Optional[str] = Field(None, description="Outer dimension unit (mm/in)")
    tags: Optional[List[str]] = Field(None, description="List of tag names")
    custom_fields: Optional[Dict] = Field(None, description="Custom fields")