from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Lead(BaseModel):
    id: Optional[int] = None
    name: str
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class LeadDetails(BaseModel):
    id: Optional[int] = None
    lead_id: int
    budget: Optional[str] = None
    needs: Optional[str] = None
    product_interest: Optional[str] = None
    timeline: Optional[str] = None


class Conversation(BaseModel):
    id: Optional[int] = None
    lead_id: int
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None


class Message(BaseModel):
    id: Optional[int] = None
    conversation_id: int
    sender: str  # 'agent' o 'lead'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class FullLead(BaseModel):
    lead: Lead
    details: Optional[LeadDetails] = None
    conversations: List[Conversation] = []