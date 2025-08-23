"""
RFC 5424 Syslog 메시지 생성기 모듈

이 모듈은 RFC 5424 표준을 따르는 Syslog 메시지를 생성하는 기능을 제공합니다.
Syslog 메시지는 우선순위, 타임스탬프, 호스트 이름, 애플리케이션 이름, 프로세스 ID,
메시지 ID, 구조화된 데이터, 그리고 메시지 본문으로 구성됩니다.
"""
import datetime
from app.models import MessageComponents


class RFC5424MessageGenerator:
    """RFC 5424 형식의 시스템 로그 메시지를 생성하는 클래스  
    
    이 클래스는 시스템 로그 메시지를 RFC 5424 형식에 맞게 생성하는 기능을 제공합니다. 
    로그 메시지는 우선순위, 버전, 타임스탬프, 호스트명, 애플리케이션 이름, 프로세스 ID, 
    메시지 ID, 구조화된 데이터 및 실제 메시지 내용으로 구성됩니다.
    """
    @staticmethod
    def generate_priority(facility: int, severity: int) -> int:
        """facility와 severity 값으로 priority 계산  
        RFC 3164 형식의 syslog 메시지에서 facility와 severity 값을 결합하여 priority 값을 계산하여 리턴합니다.

        Args:
            facility (int): 시설 코드
            severity (int): 심각도 코드

        Returns:
            int: 생성된 우선순위 값
        """
        return (facility << 3) + severity

    @staticmethod
    def generate_timestamp() -> str:
        """RFC5424 형식의 타임스탬프 생성  
        
        이 함수는 현재 시간을 ISO 8601 형식으로 변환하고, 
        RFC5424 사양에 맞게 Z 문자를 추가하여 타임스탬프를 생성합니다. 
        반환된 타임스탬프는 로깅 시스템에서 사용할 수 있는 표준 형식입니다.
        
        Returns:
            str: RFC5424 호환형 타임스탬프 문자열 (예: "2023-12-01T10:30:45.123456Z")
        """
        return datetime.datetime.now().isoformat() + "Z"

    def generate(self, components: MessageComponents) -> str:
        """RFC 5424 형식의 syslog 메시지 생성  
        
        이 함수는 주어진 메시지 구성 요소들을 기반으로 RFC 5424 규격에 따라
        syslog 메시지를 생성합니다. 우선순위, 버전, 타임스탬프, 호스트명,
        애플리케이션 이름, 프로세스 ID, 메시지 ID, 구조화된 데이터 및 메시지 내용을
        포함합니다. 필요한 구성 요소가 누락된 경우 기본값이 사용됩니다.
        
        Args:
            components (MessageComponents): syslog 메시지 구성 요소들
                - priority: 우선순위 (선택적)
                - facility: 시설 코드 (선택적)
                - severity: 심각도 (선택적)
                - timestamp: 타임스탬프 (선택적)
                - hostname: 호스트명 (선택적)
                - app_name: 애플리케이션 이름 (선택적)
                - proc_id: 프로세스 ID (선택적)
                - msg_id: 메시지 ID (선택적)
                - structured_data: 구조화된 데이터 (선택적)
                - message: 메시지 내용 (선택적)
                
        Returns:
            str: RFC 5424 형식의 syslog 메시지 문자열
            
        Example:
            >>> generator = Rfc5424Generator()
            >>> components = MessageComponents(
            ...     facility=1, severity=6, message="Test message"
            ... )
            >>> generator.generate(components)
            '<14>1 2023-01-01T00:00:00Z localhost - - - - Test message'
        """
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
