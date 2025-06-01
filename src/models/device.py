"""
Pydantic models for device-related operations.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class DeviceFilterParameters(BaseModel):
    """Query parameters for filtering devices."""
    name: Optional[str] = Field(None, description="Device name (supports regex)")
    site: Optional[str] = Field(None, description="Site name or ID (e.g., 'SF1', 'NYC1', 'DEN1')")
    role: Optional[str] = Field(None, description="Device role (e.g., 'office_access_switch', 'router', 'net-wireless-accesspoint')")
    status: Optional[str] = Field(None, description="Device status (e.g., 'active', 'planned')")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    model: Optional[str] = Field(None, description="Device type/model (e.g., 'C9300-48P', 'EX4400-48MP')")
    tag: Optional[str] = Field(None, description="Tag name (e.g., 'network', 'access-switch')")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")


class DeviceQuery(BaseModel):
    """Natural language query structure for devices."""
    query: str = Field(..., min_length=3, description="Natural language query about devices")


class DeviceSummary(BaseModel):
    """Simplified device information model."""
    id: int
    name: str
    site: str
    role: str
    status: str
    model: str
    ip_address: Optional[str] = None
    serial: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []