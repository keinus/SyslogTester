from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class CustomExample(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    rfc_version: str  # "3164" or "5424"
    raw_message: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CreateExampleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    rfc_version: str
    raw_message: str


class UpdateExampleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rfc_version: Optional[str] = None
    raw_message: Optional[str] = None


class ExampleResponse(BaseModel):
    success: bool
    example: Optional[CustomExample] = None
    examples: Optional[List[CustomExample]] = None
    error: Optional[str] = None