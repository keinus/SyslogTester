"""
RFC 3164 Syslog 메시지 생성기

이 모듈은 RFC 3164 표준에 따라 Syslog 메시지를 생성하는 기능을 제공합니다.
Syslog 메시지는 우선순위, 타임스탬프, 호스트명, 태그, PID 및 메시지 내용으로 구성됩니다.
"""
import datetime
from app.models import MessageComponents


class RFC3164MessageGenerator:
    """RFC 3164 Syslog 메시지 생성기."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

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
        """현재 시간을 RFC 3164 형식의 문자열로 생성  
        
        이 함수는 현재 시각을 기준으로 RFC 3164 로그 형식에 맞춘 시간 문자열을 생성합니다.
        형식은 "MMM DD HH:MM:SS"이며, 월 이름은 3자리 약어로 표현됩니다.
        예: "Jan  1 12:30:45"
        
        Returns:
            str: RFC 3164 형식의 시간 문자열
        """
        now = datetime.datetime.now()
        month = f"{RFC3164MessageGenerator.months[now.month-1]}"
        return f"{month} {now.day:2d} {now.strftime('%H:%M:%S')}"

    def generate(self, components: MessageComponents) -> str:
        """RFC3164 형식의 syslog 메시지 생성  

        주어진 메시지 구성 요소들을 기반으로 RFC3164 규격에 맞춘 syslog 메시지를 생성합니다.
        우선순위는 컴포넌트에서 제공되지 않을 경우 기본값(시설 4, 심각도 2)을 사용합니다.
        타임스탬프는 컴포넌트에서 제공되지 않을 경우 현재 시간을 사용합니다.
        호스트명은 컴포넌트에서 제공되지 않을 경우 'localhost'를 사용합니다.
        태그는 컴포넌트에서 제공되지 않을 경우 'app'을 사용합니다.
        프로세스 ID는 존재할 경우 '[PID]' 형식으로 포함됩니다.

        Args:
            components (MessageComponents): syslog 메시지 구성 요소들
                - priority: 우선순위 값 (선택)
                - facility: 시설 코드 (선택)
                - severity: 심각도 코드 (선택)
                - timestamp: 타임스탬프 (선택)
                - hostname: 호스트명 (선택)
                - tag: 태그 (선택)
                - pid: 프로세스 ID (선택)
                - message: 메시지 내용 (선택)

        Returns:
            str: RFC3164 형식의 syslog 메시지
        """
        priority = components.priority
        if priority is None and components.facility is not None and components.severity is not None:
            priority = self.generate_priority(
                components.facility, components.severity)

        if priority is None:
            priority = 34  # Default: facility 4, severity 2

        timestamp = components.timestamp if components.timestamp else self.generate_timestamp()
        hostname = components.hostname or "localhost"
        tag = components.tag or "app"
        pid_str = f"[{components.pid}]" if components.pid else ""
        message = components.message or ""

        return f"<{priority}>{timestamp} {hostname} {tag}{pid_str}: {message}"
