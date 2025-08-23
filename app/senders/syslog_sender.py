"""
Syslog 메시지 전송 모듈.

이 모듈은 UDP 또는 TCP 프로토콜을 사용하여 syslog 메시지를 원격 서버로 전송하는 기능을 제공합니다.
"""
import socket


class SyslogSender:
    """Syslog message sender."""
    @staticmethod
    async def send(protocol: str, message: str, host: str, port: int) -> None:
        """Syslog 메시지를 UDP 또는 TCP 프로토콜을 사용하여 전송

        주어진 프로토콜에 따라 적절한 전송 방식으로 메시지를 전송하며,
        지원되지 않는 프로토콜인 경우 ValueError를 발생시킨다.
        UDP 전송은 send_udp 메서드를, TCP 전송은 send_tcp 메서드를 호출한다.

        Args:
            protocol (str): 전송에 사용할 프로토콜 (udp 또는 tcp)
            message (str): 전송할 syslog 메시지
            host (str): 수신 호스트 주소
            port (int): 수신 포트 번호

        Raises:
            ValueError: 지원되지 않는 프로토콜이 입력된 경우
        """
        if protocol == "udp":
            await SyslogSender.send_udp(message, host, port)
        elif protocol == "tcp":
            await SyslogSender.send_tcp(message, host, port)
        else:
            raise ValueError("Protocol must be 'udp' or 'tcp'")

    @staticmethod
    async def send_udp(message: str, host: str, port: int) -> bool:
        """UDP를 통해 메시지를 전송

        메시지를 지정된 호스트와 포트로 UDP 소켓을 사용하여 전송합니다. 전송 성공 시 True를 반환하고,
        전송 중 오류가 발생하면 ConnectionError 예외를 발생시킵니다. 소켓은 전송 후 자동으로 닫힙니다.

        Args:
            message (str): 전송할 메시지 내용
            host (str): 수신 호스트 주소
            port (int): 수신 포트 번호

        Raises:
            ConnectionError: UDP 전송 실패 시 발생하는 예외

        Returns:
            bool: 전송 성공 시 True, 실패 시 False를 반환하지만 실제로는 예외가 발생함
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5.0)

            sock.sendto(message.encode('utf-8'), (host, port))
            sock.close()

            print(f"UDP message sent to {host}:{port}")
            return True

        except (socket.error, OSError) as e:
            print(f"UDP send failed: {e}")
            raise ConnectionError(f"UDP send failed: {e}") from e

    @staticmethod
    async def send_tcp(message: str, host: str, port: int) -> bool:
        """TCP를 통해 메시지를 전송

        주어진 호스트와 포트로 TCP 소켓을 생성하여 메시지를 전송합니다. 전송 성공 시 True를 반환하고,
        실패할 경우 ConnectionError 예외를 발생시킵니다. 소켓 연결 타임아웃은 5초로 설정됩니다.

        Args:
            message (str): 전송할 메시지 내용
            host (str): 메시지를 전송할 호스트 주소
            port (int): 메시지를 전송할 포트 번호

        Raises:
            ConnectionError: 소켓 연결 또는 전송 과정에서 오류가 발생한 경우

        Returns:
            bool: 전송 성공 시 True, 실패 시 False
        """
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
            raise ConnectionError(f"TCP send failed: {e}") from e
