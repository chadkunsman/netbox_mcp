"""
Pydantic models for circuit-related operations.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class CircuitFilterParameters(BaseModel):
    """Query parameters for filtering circuits."""
    cid: Optional[str] = Field(None, description="Circuit ID - exact match")
    cid_contains: Optional[str] = Field(None, description="Circuit ID pattern match (case-insensitive contains search)")
    search: Optional[str] = Field(None, description="Cross-field search across CID, provider, description, and terminations")
    provider: Optional[str] = Field(None, description="Provider name or ID")
    type: Optional[str] = Field(None, description="Circuit type (e.g., 'Internet', 'MPLS', 'Point-to-Point')")
    status: Optional[str] = Field(None, description="Circuit status (e.g., 'active', 'planned', 'provisioning')")
    site: Optional[str] = Field(None, description="Site name or ID where circuit terminates")
    tenant: Optional[str] = Field(None, description="Tenant name or ID")
    description: Optional[str] = Field(None, description="Circuit description (supports partial match)")
    tag: Optional[str] = Field(None, description="Tag name")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")


class CircuitQuery(BaseModel):
    """Natural language query structure for circuits."""
    query: str = Field(..., min_length=3, description="Natural language query about circuits")


class CircuitSummary(BaseModel):
    """Simplified circuit information model."""
    id: int
    cid: str
    provider: str
    type: str
    status: str
    description: Optional[str] = None
    install_date: Optional[str] = None
    commit_rate: Optional[int] = None  # In kbps
    tenant: Optional[str] = None
    termination_a: Optional[str] = None  # Site A
    termination_z: Optional[str] = None  # Site Z
    tags: List[str] = []