from typing import Optional, Union
from pydantic import BaseModel


class SyslogMessage(BaseModel):
    priority: int
    facility: int
    severity: int
    timestamp: str
    hostname: str
    tag: str
    pid: Optional[int] = None
    message: str
    rfc_version: str = "3164"


class RFC5424SyslogMessage(BaseModel):
    priority: int
    facility: int
    severity: int
    version: int = 1
    timestamp: str
    hostname: str
    app_name: Optional[str] = None
    proc_id: Optional[str] = None
    msg_id: Optional[str] = None
    structured_data: Optional[str] = None
    message: str
    rfc_version: str = "5424"


class MessageComponents(BaseModel):
    rfc_version: str  # "3164" or "5424"
    priority: Optional[int] = None
    facility: Optional[int] = None
    severity: Optional[int] = None
    timestamp: Optional[str] = None
    hostname: Optional[str] = None
    # RFC 3164 specific
    tag: Optional[str] = None
    pid: Optional[int] = None
    # RFC 5424 specific
    app_name: Optional[str] = None
    proc_id: Optional[str] = None
    msg_id: Optional[str] = None
    structured_data: Optional[str] = None
    # Common
    message: Optional[str] = None


class SyslogRequest(BaseModel):
    raw_message: str
    target_server: str
    target_port: int = 514
    protocol: str = "udp"
    rfc_version: str = "3164"


class GenerateRequest(BaseModel):
    components: MessageComponents
    target_server: str
    target_port: int = 514
    protocol: str = "udp"


class SyslogResponse(BaseModel):
    success: bool
    parsed_message: Optional[Union[SyslogMessage, RFC5424SyslogMessage]] = None
    error: Optional[str] = None
    sent_to: Optional[str] = None
    generated_message: Optional[str] = None