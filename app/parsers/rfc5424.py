"""RFC 5424 Syslog 메시지 파서.

이 모듈은 RFC 5424 형식의 syslog 메시지를 파싱하여 
메시지의 각 필드를 추출하고, RFC5424SyslogMessage 객체로 반환한다.
"""
import re
from app.models import RFC5424SyslogMessage


class RFC5424Parser:
    """RFC 5424 형식의 시스로그 메시지를 파싱하는 클래스  
    
    이 클래스는 RFC 5424 표준에 따라 시스로그 메시지를 구문 분석하고,
    필요한 정보를 추출하여 RFC5424SyslogMessage 객체로 반환합니다.
    """

    RFC5424_PATTERN = re.compile(
        r'^<(\d+)>'  # Priority
        r'(\d+)\s+'  # Version
        r'(\S+)\s+'  # Timestamp
        r'(\S+)\s+'  # Hostname
        r'(\S+)\s+'  # App-Name
        r'(\S+)\s+'  # ProcID
        r'(\S+)\s+'  # MsgID
        r'(-|\[.*?\](?:\[.*?\])*)\s*'  # Structured-Data (can be "-" or one/more [SD elements])
        r'(.*)$'     # Message
    )
    """RFC 5424 형식을 위한 정규 표현식 패턴"""


    @staticmethod
    def parse_priority(priority: int) -> tuple:
        """RFC 5424 우선순위 값을 파싱하여 시설과 심각도로 분리

        주어진 우선순위 정수에서 시설(facility)과 심각도(severity)를 추출합니다.
        시설은 우선순위 값을 3비트 오른쪽 시프트하여 계산되며,
        심각도는 우선순위 값과 7(0b111)의 비트 AND 연산으로 계산됩니다.

        Args:
            priority (int): RFC 5424 형식의 우선순위 값

        Returns:
            tuple: (facility, severity) 튜플로 구성된 결과
        """
        facility = priority >> 3
        severity = priority & 7
        return facility, severity

    def parse(self, raw_message: str) -> RFC5424SyslogMessage:
        """RFC 5424 형식의 원시 메시지를 파싱하여 구조화된 메시지로 변환

        주어진 원시 syslog 메시지를 RFC 5424 표준에 따라 파싱하고, 필요한 필드들을 추출하여
        RFC5424SyslogMessage 객체로 반환한다. 파싱 과정에서 형식이 잘못된 경우 ValueError를 발생시킨다.
        nil 값 처리를 위해 "-" 문자열은 None으로 변환된다.

        Args:
            raw_message (str): 파싱할 RFC 5424 형식의 원시 syslog 메시지

        Raises:
            ValueError: 입력 메시지가 RFC 5424 형식이 아닌 경우
            ValueError: 메시지 필드 파싱 중 오류가 발생한 경우

        Returns:
            RFC5424SyslogMessage: 파싱된 syslog 메시지 정보를 담은 객체
        """
        match = self.RFC5424_PATTERN.match(raw_message.strip())

        if not match:
            raise ValueError("Invalid RFC 5424 syslog format")

        priority_str, version_str, timestamp_str, hostname,\
            app_name, proc_id, msg_id, structured_data, message = match.groups()

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
                pid=proc_id,
                msg_id=msg_id,
                structured_data=structured_data,
                message=message
            )

        except ValueError as e:
            raise ValueError(f"Parsing error: {e}") from e
