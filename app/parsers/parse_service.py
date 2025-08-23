"""Parser service"""
from app.models import SyslogMessage
from app.parsers import RFC3164Parser, RFC5424Parser


rfc3164_parser = RFC3164Parser()
"""RFC3164Parser: RFC3164 형식 syslog 메시지를 파싱하는 인스턴스"""

rfc5424_parser = RFC5424Parser()
"""RFC5424Parser: RFC5424 형식 syslog 메시지를 파싱하는 인스턴스"""

def parse(version: str, msg: str) -> SyslogMessage:
    """지정된 버전에 따라 syslog 메시지를 파싱합니다.

    Args:
        version (str): 파싱할 메시지의 버전으로, "5424" 또는 다른 값이 될 수 있습니다.
        msg (str): 파싱할 syslog 메시지 문자열입니다.

    Returns:
        SyslogMessage: 파싱된 syslog 메시지 객체를 반환합니다.
    """
    parsed_message: SyslogMessage
    if version == "5424":
        parsed_message = rfc5424_parser.parse(msg)
    else:
        parsed_message = rfc3164_parser.parse(msg)
    print(f"Message parsed successfully: {parsed_message}")
    return parsed_message
