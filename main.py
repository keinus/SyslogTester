from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socket
import re
import datetime
from typing import Optional, Dict, Any
import json
import asyncio
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="RFC 3164 Syslog Parser", version="1.0.0")
app.mount("/static", StaticFiles(directory="./claude/static"), name="static")

# CORS 설정
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

class SyslogRequest(BaseModel):
    raw_message: str
    target_server: str
    target_port: int = 514
    protocol: str = "udp"  # udp or tcp

class SyslogResponse(BaseModel):
    success: bool
    parsed_message: Optional[SyslogMessage] = None
    error: Optional[str] = None
    sent_to: Optional[str] = None

class RFC3164Parser:
    """RFC 3164 Syslog 메시지 파서"""
    
    # 월 이름 매핑
    MONTHS = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    # RFC 3164 패턴: <Priority>Timestamp Hostname Tag[PID]: Message
    RFC3164_PATTERN = re.compile(
        r'^<(\d+)>'  # Priority
        r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'  # Timestamp
        r'(\S+)\s+'  # Hostname
        r'([^:\[\s]+)(?:\[(\d+)\])?:\s*'  # Tag[PID]:
        r'(.*)$'  # Message
    )
    
    @staticmethod
    def parse_priority(priority: int) -> tuple:
        """Priority에서 Facility와 Severity 추출"""
        facility = priority >> 3
        severity = priority & 7
        return facility, severity
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> str:
        """RFC 3164 타임스탬프를 ISO 형식으로 변환"""
        try:
            # "Oct 11 22:14:15" 형식 파싱
            parts = timestamp_str.split()
            month_name = parts[0]
            day = int(parts[1])
            time_part = parts[2]
            
            month = RFC3164Parser.MONTHS.get(month_name)
            if not month:
                raise ValueError(f"Invalid month: {month_name}")
            
            # 현재 년도 사용 (RFC 3164는 년도를 포함하지 않음)
            year = datetime.datetime.now().year
            
            # 시간 파싱
            hour, minute, second = map(int, time_part.split(':'))
            
            dt = datetime.datetime(year, month, day, hour, minute, second)
            return dt.isoformat()
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid timestamp format: {e}")
    
    def parse(self, raw_message: str) -> SyslogMessage:
        """RFC 3164 메시지 파싱"""
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

class SyslogSender:
    """Syslog 메시지 전송기"""
    
    @staticmethod
    async def send_udp(message: str, host: str, port: int) -> bool:
        """UDP로 syslog 메시지 전송"""
        try:
            loop = asyncio.get_event_loop()
            
            # 비동기 UDP 소켓 생성
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)
            
            # 메시지 전송
            sock.sendto(message.encode('utf-8'), (host, port))
            sock.close()
            
            print(f"✅ UDP Message sent to {host}:{port}")
            return True
            
        except Exception as e:
            print(f"❌ UDP send failed: {e}")
            raise Exception(f"UDP send failed: {e}")
    
    @staticmethod
    async def send_tcp(message: str, host: str, port: int) -> bool:
        """TCP로 syslog 메시지 전송"""
        try:
            loop = asyncio.get_event_loop()
            
            # 비동기 TCP 소켓 생성
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            # 서버 연결 및 메시지 전송
            sock.connect((host, port))
            sock.send(message.encode('utf-8'))
            sock.close()
            
            print(f"✅ TCP Message sent to {host}:{port}")
            return True
            
        except Exception as e:
            print(f"❌ TCP send failed: {e}")
            raise Exception(f"TCP send failed: {e}")

# 파서와 전송기 인스턴스
parser = RFC3164Parser()
sender = SyslogSender()

@app.post("/parse", response_model=SyslogResponse)
async def parse_syslog(request: SyslogRequest):
    """Syslog 메시지 파싱 및 전송"""
    print(f"📨 Received request: {request}")
    
    try:
        # 메시지 파싱
        parsed_message = parser.parse(request.raw_message)
        print(f"✅ Message parsed successfully: {parsed_message}")
        
        # 서버로 전송
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
        
        print(f"✅ Response: {response}")
        return response
        
    except ValueError as e:
        print(f"❌ Validation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        print(f"❌ Transmission error: {e}")
        return SyslogResponse(
            success=False,
            error=f"Transmission error: {str(e)}"
        )

@app.post("/parse-only", response_model=SyslogResponse)
async def parse_only(raw_message: str = Form(...)):
    """Syslog 메시지 파싱만 수행 (전송 없음)"""
    print(f"📝 Parse-only request: {raw_message}")
    
    try:
        parsed_message = parser.parse(raw_message)
        print(f"✅ Parse-only successful: {parsed_message}")
        
        response = SyslogResponse(
            success=True,
            parsed_message=parsed_message
        )
        
        return response
        
    except ValueError as e:
        print(f"❌ Parse-only error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )

@app.get("/validate/{message}")
async def validate_format(message: str):
    """RFC 3164 형식 유효성 검사"""
    try:
        parsed = parser.parse(message)
        return {
            "valid": True,
            "parsed": parsed.dict()
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

# 테스트용 syslog 서버 시뮬레이터
@app.post("/test-server/{port}")
async def start_test_server(port: int):
    """테스트용 syslog 서버 시작 (UDP)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', port))
        sock.settimeout(1.0)
        
        print(f"🔄 Test server listening on port {port}")
        
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"📨 Test server received: {message} from {addr}")
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
async def root():
    """API 정보"""
    return {
        "title": "RFC 3164 Syslog Parser API",
        "version": "1.0.0",
        "description": "Parse and send RFC 3164 syslog messages",
        "endpoints": {
            "POST /parse": "Parse and send syslog message",
            "POST /parse-only": "Parse syslog message only",
            "GET /validate/{message}": "Validate RFC 3164 format",
            "POST /test-server/{port}": "Start test syslog server"
        },
        "example_message": "<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8",
        "frontend_url": "Open index.html in your browser"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RFC 3164 Syslog Parser Backend...")
    print("🔧 API available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("📄 Open index.html in your browser for frontend")
    uvicorn.run(app, host="0.0.0.0", port=8000)