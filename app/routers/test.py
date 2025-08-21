import socket
from fastapi import APIRouter

router = APIRouter(prefix="/api/test", tags=["test"])


@router.post("/test-server/{port}")
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