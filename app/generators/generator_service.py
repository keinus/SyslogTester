"""Syslog Generate Service"""
from app.generators import RFC3164MessageGenerator, RFC5424MessageGenerator
from app.models.syslog import MessageComponents

rfc3164_generator = RFC3164MessageGenerator()
"""RFC3164MessageGenerator: RFC3164 형식 syslog 메시지를 생성하는 인스턴스"""

rfc5424_generator = RFC5424MessageGenerator()
"""RFC5424MessageGenerator: RFC5424 형식 syslog 메시지를 생성하는 인스턴스"""


def generate(rfc_version: str, components: MessageComponents) -> str:
    """RFC 버전에 따라 메시지를 생성합니다.

    Args:
        rfc_version (str): 사용할 RFC 버전으로, "5424" 또는 다른 값이 될 수 있습니다.
        components (MessageComponents): 메시지 생성에 필요한 구성 요소들

    Returns:
        str: 생성된 메시지 문자열
    """
    generated_message: str
    if rfc_version == "5424":
        generated_message = rfc5424_generator.generate(components)
    else:
        generated_message = rfc3164_generator.generate(components)

    print(f"Generated message: {generated_message}")
    return generated_message
