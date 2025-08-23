"""
RFC 3164 Syslog 메시지 파서 모듈.

이 모듈은 RFC 3164 형식의 syslog 메시지를 파싱하여
SyslogMessage 객체로 변환하는 기능을 제공한다.
"""
import datetime
import re
from app.models import RFC3164SyslogMessage


class RFC3164Parser:
    """RFC 3164 형식의 로그 메시지를 파싱하는 클래스입니다."""

    MONTHS = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    """월 이름을 숫자로 매핑하는 딕셔너리입니다."""

    RFC3164_PATTERN = re.compile(
        r'^<(\d+)>'
        r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(\S+)\s+'
        r'([^:\[\s]+)(?:\[(\d+)\])?:\s*'
        r'(.*)$'
    )
    """RFC 3164 로그 형식을 파싱하기 위한 정규 표현식입니다."""

    @staticmethod
    def parse_priority(priority: int) -> tuple:
        """설정 우선순위를 시설 코드와 심각도로 분리  

        주어진 우선순위 정수를 비트 연산을 통해 시설(facility) 코드와 심각도(severity)로 분리합니다.
        시설 코드는 우선순위의 상위 5비트(>> 3)로 계산되며, 심각도는 하위 3비트(& 7)로 계산됩니다.

        Args:
            priority (int): RFC 3164 형식의 시스템 로그 우선순위 값

        Returns:
            tuple: (facility: int, severity: int) 튜플로 구성된 분리된 우선순위 정보
        """
        facility = priority >> 3
        severity = priority & 7
        return facility, severity

    @staticmethod
    def parse_timestamp(timestamp_str: str) -> str:
        """RFC3164 형식의 타임스탬프 문자열을 ISO 형식으로 변환  

        주어진 RFC3164 형식의 타임스탬프 문자열을 파싱하여 ISO 8601 형식의 문자열로 반환한다.
        형식은 "MMM DD HH:MM:SS" 또는 "MMM DD HH:MM" 형태를 지원하며, 
        연도 정보는 현재 연도로 설정된다. 월 이름은 영문 약어(예: Jan, Feb)로 주어져야 하며,
        유효하지 않은 월 이름이나 시간 형식일 경우 ValueError 예외를 발생시킨다.

        Args:
            timestamp_str (str): RFC3164 형식의 타임스탬프 문자열

        Raises:
            ValueError: 월 이름이 유효하지 않거나 시간 형식이 잘못된 경우
            ValueError: 타임스탬프 파싱 중 오류가 발생한 경우

        Returns:
            str: ISO 8601 형식의 타임스탬프 문자열
        """
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
            raise ValueError(f'Invalid timestamp format: {e}') from e

    def parse(self, raw_message: str) -> RFC3164SyslogMessage:
        """RFC 3164 형식의 원시 메시지를 파싱  
        주어진 RFC 3164 형식의 원시 시스템 로그 메시지를 분석하여 SyslogMessage 객체로 변환한다. 
        메시지 형식이 유효하지 않거나 파싱 중에 오류가 발생하면 ValueError 예외를 발생시킨다.

        Args:
            raw_message (str): 파싱할 RFC 3164 형식의 원시 메시지

        Raises:
            ValueError: 메시지 형식이 유효하지 않거나 파싱 중 오류가 발생한 경우

        Returns:
            SyslogMessage: 파싱된 시스템 로그 메시지 정보를 담은 객체
        """
        match = self.RFC3164_PATTERN.match(raw_message.strip())

        if not match:
            raise ValueError("Invalid RFC 3164 syslog format")

        priority_str, timestamp_str, hostname, tag, pid_str, message = match.groups()

        try:
            priority = int(priority_str)
            facility, severity = self.parse_priority(priority)
            timestamp = self.parse_timestamp(timestamp_str)
            pid = pid_str if pid_str else None

            return RFC3164SyslogMessage(
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
            raise ValueError(f'Parsing error: {e}') from e
