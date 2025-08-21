import socket


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