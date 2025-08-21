import datetime
import re
import socket
from typing import Optional, Union, Dict, Any

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="RFC 3164/5424 Syslog Parser", version="1.0.0")
app.mount("/static", StaticFiles(directory="./static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class RFC3164Parser:
    """RFC 3164 Syslog message parser."""
    
    MONTHS = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    RFC3164_PATTERN = re.compile(
        r'^<(\d+)>'
        r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(\S+)\s+'
        r'([^:\[\s]+)(?:\[(\d+)\])?:\s*'
        r'(.*)$'
    )
    
    @staticmethod
    def parse_priority(priority: int) -> tuple:
        """Extract facility and severity from priority."""
        facility = priority >> 3
        severity = priority & 7
        return facility, severity
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> str:
        """Convert RFC 3164 timestamp to ISO format."""
        try:
            parts = timestamp_str.split()
            month_name = parts[0]
            day = int(parts[1])
            time_part = parts[2]
            
            month = RFC3164Parser.MONTHS.get(month_name)
            if not month:
                raise ValueError(f"Invalid month: {month_name}")
            
            year = datetime.datetime.now().year
            hour, minute, second = map(int, time_part.split(':'))
            
            dt = datetime.datetime(year, month, day, hour, minute, second)
            return dt.isoformat()
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid timestamp format: {e}")
    
    def parse(self, raw_message: str) -> SyslogMessage:
        """Parse RFC 3164 message."""
        match = self.RFC3164_PATTERN.match(raw_message.strip())
        
        if not match:
            raise ValueError("Invalid RFC 3164 syslog format")
        
        priority_str, timestamp_str, hostname, tag, pid_str, message = match.groups()
        
        try:
            priority = int(priority_str)
            facility, severity = self.parse_priority(priority)
            timestamp = self.parse_timestamp(timestamp_str)
            pid = int(pid_str) if pid_str else None
            
            return SyslogMessage(
                priority=priority,
                facility=facility,
                severity=severity,
                timestamp=timestamp,
                hostname=hostname,
                tag=tag,
                pid=pid,
                message=message
            )
            
        except ValueError as e:
            raise ValueError(f"Parsing error: {e}")


class RFC5424Parser:
    """RFC 5424 Syslog message parser."""
    
    RFC5424_PATTERN = re.compile(
        r'^<(\d+)>'  # Priority
        r'(\d+)\s+'  # Version
        r'(\S+)\s+'  # Timestamp
        r'(\S+)\s+'  # Hostname
        r'(\S+)\s+'  # App-Name
        r'(\S+)\s+'  # ProcID
        r'(\S+)\s+'  # MsgID
        r'(\S+)\s*'  # Structured-Data
        r'(.*)$'     # Message
    )
    
    @staticmethod
    def parse_priority(priority: int) -> tuple:
        """Extract facility and severity from priority."""
        facility = priority >> 3
        severity = priority & 7
        return facility, severity
    
    def parse(self, raw_message: str) -> RFC5424SyslogMessage:
        """Parse RFC 5424 message."""
        match = self.RFC5424_PATTERN.match(raw_message.strip())
        
        if not match:
            raise ValueError("Invalid RFC 5424 syslog format")
        
        priority_str, version_str, timestamp_str, hostname, app_name, proc_id, msg_id, structured_data, message = match.groups()
        
        try:
            priority = int(priority_str)
            version = int(version_str)
            facility, severity = self.parse_priority(priority)
            
            # Handle nil values
            app_name = None if app_name == "-" else app_name
            proc_id = None if proc_id == "-" else proc_id
            msg_id = None if msg_id == "-" else msg_id
            structured_data = None if structured_data == "-" else structured_data
            
            return RFC5424SyslogMessage(
                priority=priority,
                facility=facility,
                severity=severity,
                version=version,
                timestamp=timestamp_str,
                hostname=hostname,
                app_name=app_name,
                proc_id=proc_id,
                msg_id=msg_id,
                structured_data=structured_data,
                message=message
            )
            
        except ValueError as e:
            raise ValueError(f"Parsing error: {e}")


class RFC3164MessageGenerator:
    """RFC 3164 Syslog message generator."""
    
    @staticmethod
    def generate_priority(facility: int, severity: int) -> int:
        """Generate priority from facility and severity."""
        return (facility << 3) + severity
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate RFC 3164 timestamp."""
        now = datetime.datetime.now()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f"{months[now.month-1]} {now.day:2d} {now.strftime('%H:%M:%S')}"
    
    def generate(self, components: MessageComponents) -> str:
        """Generate RFC 3164 message from components."""
        priority = components.priority
        if priority is None and components.facility is not None and components.severity is not None:
            priority = self.generate_priority(components.facility, components.severity)
        
        if priority is None:
            priority = 34  # Default: facility 4, severity 2
        
        timestamp = components.timestamp if components.timestamp else self.generate_timestamp()
        hostname = components.hostname or "localhost"
        tag = components.tag or "app"
        pid_str = f"[{components.pid}]" if components.pid else ""
        message = components.message or ""
        
        return f"<{priority}>{timestamp} {hostname} {tag}{pid_str}: {message}"


class RFC5424MessageGenerator:
    """RFC 5424 Syslog message generator."""
    
    @staticmethod
    def generate_priority(facility: int, severity: int) -> int:
        """Generate priority from facility and severity."""
        return (facility << 3) + severity
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate RFC 5424 timestamp (ISO 8601)."""
        return datetime.datetime.now().isoformat() + "Z"
    
    def generate(self, components: MessageComponents) -> str:
        """Generate RFC 5424 message from components."""
        priority = components.priority
        if priority is None and components.facility is not None and components.severity is not None:
            priority = self.generate_priority(components.facility, components.severity)
        
        if priority is None:
            priority = 34  # Default: facility 4, severity 2
        
        version = 1
        timestamp = components.timestamp if components.timestamp else self.generate_timestamp()
        hostname = components.hostname or "localhost"
        app_name = components.app_name or "-"
        proc_id = components.proc_id or "-"
        msg_id = components.msg_id or "-"
        structured_data = components.structured_data or "-"
        message = components.message or ""
        
        return f"<{priority}>{version} {timestamp} {hostname} {app_name} {proc_id} {msg_id} {structured_data} {message}"


class SyslogSender:
    """Syslog message sender."""
    
    @staticmethod
    async def send_udp(message: str, host: str, port: int) -> bool:
        """Send syslog message via UDP."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)
            
            sock.sendto(message.encode('utf-8'), (host, port))
            sock.close()
            
            print(f"UDP message sent to {host}:{port}")
            return True
            
        except (socket.error, OSError) as e:
            print(f"UDP send failed: {e}")
            raise ConnectionError(f"UDP send failed: {e}")
    
    @staticmethod
    async def send_tcp(message: str, host: str, port: int) -> bool:
        """Send syslog message via TCP."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            sock.connect((host, port))
            sock.send(message.encode('utf-8'))
            sock.close()
            
            print(f"TCP message sent to {host}:{port}")
            return True
            
        except (socket.error, OSError) as e:
            print(f"TCP send failed: {e}")
            raise ConnectionError(f"TCP send failed: {e}")

rfc3164_parser = RFC3164Parser()
rfc5424_parser = RFC5424Parser()
rfc3164_generator = RFC3164MessageGenerator()
rfc5424_generator = RFC5424MessageGenerator()
sender = SyslogSender()

@app.post("/parse", response_model=SyslogResponse)
async def parse_syslog(request: SyslogRequest):
    """Parse and send syslog message."""
    print(f"Received request: {request}")
    
    try:
        # Select parser based on RFC version
        if request.rfc_version == "5424":
            parsed_message = rfc5424_parser.parse(request.raw_message)
        else:
            parsed_message = rfc3164_parser.parse(request.raw_message)
        print(f"Message parsed successfully: {parsed_message}")
        
        if request.protocol.lower() == "udp":
            await sender.send_udp(request.raw_message, request.target_server, request.target_port)
        elif request.protocol.lower() == "tcp":
            await sender.send_tcp(request.raw_message, request.target_server, request.target_port)
        else:
            raise ValueError("Protocol must be 'udp' or 'tcp'")
        
        response = SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            sent_to=f"{request.target_server}:{request.target_port} ({request.protocol.upper()})"
        )
        
        print(f"Response: {response}")
        return response
        
    except ValueError as e:
        print(f"Validation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        print(f"Transmission error: {e}")
        return SyslogResponse(
            success=False,
            error=f"Transmission error: {str(e)}"
        )

@app.post("/parse-only", response_model=SyslogResponse)
async def parse_only(raw_message: str = Form(...), rfc_version: str = Form("3164")):
    """Parse syslog message only (no transmission)."""
    print(f"Parse-only request: {raw_message}, RFC: {rfc_version}")
    
    try:
        # Select parser based on RFC version
        if rfc_version == "5424":
            parsed_message = rfc5424_parser.parse(raw_message)
        else:
            parsed_message = rfc3164_parser.parse(raw_message)
        print(f"Parse-only successful: {parsed_message}")
        
        return SyslogResponse(
            success=True,
            parsed_message=parsed_message
        )
        
    except ValueError as e:
        print(f"Parse-only error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )

@app.get("/validate/{message}/{rfc_version}")
async def validate_format(message: str, rfc_version: str = "3164"):
    """Validate RFC format."""
    try:
        # Select parser based on RFC version
        if rfc_version == "5424":
            parsed = rfc5424_parser.parse(message)
        else:
            parsed = rfc3164_parser.parse(message)
        return {
            "valid": True,
            "parsed": parsed.model_dump(),
            "rfc_version": rfc_version
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "rfc_version": rfc_version
        }


@app.post("/generate", response_model=SyslogResponse)
async def generate_syslog(request: GenerateRequest):
    """Generate and send syslog message from components."""
    print(f"Generate request: {request}")
    
    try:
        # Select generator based on RFC version
        if request.components.rfc_version == "5424":
            generated_message = rfc5424_generator.generate(request.components)
        else:
            generated_message = rfc3164_generator.generate(request.components)
        
        print(f"Generated message: {generated_message}")
        
        # Send the generated message
        if request.protocol.lower() == "udp":
            await sender.send_udp(generated_message, request.target_server, request.target_port)
        elif request.protocol.lower() == "tcp":
            await sender.send_tcp(generated_message, request.target_server, request.target_port)
        else:
            raise ValueError("Protocol must be 'udp' or 'tcp'")
        
        # Parse the generated message to return structured data
        if request.components.rfc_version == "5424":
            parsed_message = rfc5424_parser.parse(generated_message)
        else:
            parsed_message = rfc3164_parser.parse(generated_message)
        
        response = SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            generated_message=generated_message,
            sent_to=f"{request.target_server}:{request.target_port} ({request.protocol.upper()})"
        )
        
        print(f"Response: {response}")
        return response
        
    except ValueError as e:
        print(f"Generation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        print(f"Transmission error: {e}")
        return SyslogResponse(
            success=False,
            error=f"Transmission error: {str(e)}"
        )


@app.post("/generate-only", response_model=SyslogResponse)
async def generate_only(components: MessageComponents):
    """Generate syslog message only (no transmission)."""
    print(f"Generate-only request: {components}")
    
    try:
        # Select generator based on RFC version
        if components.rfc_version == "5424":
            generated_message = rfc5424_generator.generate(components)
            parsed_message = rfc5424_parser.parse(generated_message)
        else:
            generated_message = rfc3164_generator.generate(components)
            parsed_message = rfc3164_parser.parse(generated_message)
        
        print(f"Generated message: {generated_message}")
        
        return SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            generated_message=generated_message
        )
        
    except ValueError as e:
        print(f"Generation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )

@app.post("/test-server/{port}")
async def start_test_server(port: int):
    """Start test syslog server (UDP)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', port))
        sock.settimeout(1.0)
        
        print(f"Test server listening on port {port}")
        
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Test server received: {message} from {addr}")
            return {
                "success": True,
                "received_message": message,
                "from_address": f"{addr[0]}:{addr[1]}"
            }
        except socket.timeout:
            return {
                "success": False,
                "error": "No message received within timeout"
            }
        finally:
            sock.close()
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Test server error: {str(e)}"
        }

@app.get("/")
async def serve_index():
    """Serve the index.html file."""
    return FileResponse("./static/index.html")

@app.get("/api")
async def api_info():
    """API information."""
    return {
        "title": "RFC 3164/5424 Syslog Parser API",
        "version": "2.0.0",
        "description": "Parse and send RFC 3164/5424 syslog messages",
        "endpoints": {
            "POST /parse": "Parse and send syslog message (raw)",
            "POST /parse-only": "Parse syslog message only (raw)",
            "POST /generate": "Generate and send syslog message (from components)",
            "POST /generate-only": "Generate syslog message only (from components)",
            "GET /validate/{message}/{rfc_version}": "Validate RFC format",
            "POST /test-server/{port}": "Start test syslog server"
        },
        "rfc_versions": ["3164", "5424"],
        "example_messages": {
            "rfc3164": "<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8",
            "rfc5424": "<34>1 2003-10-11T22:14:15.003Z mymachine su - ID47 - BOM'su root' failed for lonvick on /dev/pts/8"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting RFC 3164/5424 Syslog Parser Backend...")
    print("API available at: http://localhost:8001")
    print("API documentation at: http://localhost:8001/docs")
    print("Frontend available at: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)