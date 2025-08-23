"""
RFC 3164/5424 Syslog Parser API 정보 라우터

이 모듈은 RFC 3164 및 RFC 5424 형식의 syslog 메시지를 파싱하고 생성하는
API 엔드포인트를 제공합니다. Syslog 메시지의 유효성 검사 및 테스트 서버 시작 기능도 포함됩니다.
"""

from typing import Any
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["info"])


@router.get("/")
async def api_info() -> dict[str, Any]:
    """API 정보를 반환  
    
    API의 제목, 버전, 설명, 사용 가능한 엔드포인트 목록, 지원하는 RFC 버전, 예제 메시지 등을 포함한 정보를 반환합니다.
    """
    return {
        "title": "RFC 3164/5424 Syslog Parser API",
        "version": "2.0.0",
        "description": "Parse and send RFC 3164/5424 syslog messages",
        "endpoints": {
            "POST /api/syslog/parse": "Parse and send syslog message (raw)",
            "POST /api/syslog/parse-only": "Parse syslog message only (raw)",
            "POST /api/syslog/generate": "Generate and send syslog message (from components)",
            "POST /api/syslog/generate-only": "Generate syslog message only (from components)",
            "GET /api/syslog/validate/{message}/{rfc_version}": "Validate RFC format",
            "POST /api/test/test-server/{port}": "Start test syslog server"
        },
        "rfc_versions": ["3164", "5424"],
        "example_messages": {
            "rfc3164": "<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8",
            "rfc5424": "<34>1 2003-10-11T22:14:15.003Z mymachine su - ID47 - BOM'su root' failed for lonvick on /dev/pts/8"
        }
    }