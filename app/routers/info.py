from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["info"])


@router.get("/")
async def api_info():
    """API information."""
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