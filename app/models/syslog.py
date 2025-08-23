"""Syslog Message 데이터 모델"""
from typing import Optional, Union
from pydantic import BaseModel


class SyslogMessage(BaseModel):
    """시스템 로그 메시지 공통 데이터 모델을 정의한다."""

    priority: int
    """로그 우선순위 값을 정의한다."""

    facility: int
    """로그 발생 시설(facility) 코드를 정의한다."""

    severity: int
    """로그 심각도(severity) 수준을 정의한다."""

    timestamp: str
    """로그 발생 시간 정보를 포함한 문자열 형식 타임스탬프이다."""

    hostname: str
    """로그가 발생한 호스트 이름을 정의한다."""

    pid: Optional[str] = None
    """프로세스 ID를 포함하며, 존재하지 않을 경우 None으로 설정된다."""

    message: str
    """실제 로그 내용 메시지를 정의한다."""

    rfc_version: str = "3164"
    """사용하는 RFC 버전을 지정하며, 기본값은 '3164'이다."""

class RFC3164SyslogMessage(SyslogMessage):
    """RFC 3164 형식의 시스템 로그 메시지 데이터 모델을 정의한다."""

    tag: str
    """로그 메시지를 식별하는 태그 정보를 포함한다."""


class RFC5424SyslogMessage(SyslogMessage):
    """RFC 5424 형식의 시스로그 메시지 모델을 정의한다."""

    version: int = 1
    """RFC 5424 버전 번호를 나타낸다."""

    app_name: Optional[str] = None
    """애플리케이션 이름을 나타낸다."""

    msg_id: Optional[str] = None
    """메시지 ID를 나타낸다."""

    structured_data: Optional[str] = None
    """구조화된 데이터를 나타낸다."""


class MessageComponents(BaseModel):
    """RFC 3164 및 5424 형식의 시스템 로그 메시지 구성 요소를 나타냅니다."""

    rfc_version: str  # "3164" or "5424"
    """RFC 버전 (3164 또는 5424)"""

    priority: Optional[int] = None
    """우선순위 값"""

    facility: Optional[int] = None
    """시설 코드"""

    severity: Optional[int] = None
    """심각도 수준"""

    timestamp: Optional[str] = None
    """타임스탬프"""

    hostname: Optional[str] = None
    """호스트 이름"""

    # RFC 3164 specific
    tag: Optional[str] = None
    """태그 (RFC 3164 전용)"""

    pid: Optional[int] = None
    """프로세스 ID (RFC 3164 전용)"""

    # RFC 5424 specific
    app_name: Optional[str] = None
    """애플리케이션 이름 (RFC 5424 전용)"""

    proc_id: Optional[str] = None
    """프로세스 ID (RFC 5424 전용)"""

    msg_id: Optional[str] = None
    """메시지 ID (RFC 5424 전용)"""

    structured_data: Optional[str] = None
    """구조화된 데이터 (RFC 5424 전용)"""

    # Common
    message: Optional[str] = None
    """로그 메시지 내용"""


class SyslogRequest(BaseModel):
    """Syslog 요청 데이터 모델을 정의합니다."""

    raw_message: str
    """원시 syslog 메시지 내용을 저장합니다."""

    target_server: str
    """메시지를 전송할 대상 서버 주소를 저장합니다."""

    target_port: int = 514
    """대상 서버의 포트 번호를 저장합니다. 기본값은 514입니다."""

    protocol: str = "udp"
    """전송에 사용할 프로토콜을 저장합니다. 기본값은 udp입니다."""

    rfc_version: str = "3164"
    """사용할 RFC 버전을 저장합니다. 기본값은 3164입니다."""


class GenerateRequest(BaseModel):
    """Syslog 메시지 생성 요청 데이터 모델입니다."""

    components: MessageComponents
    """메시지 구성 요소들"""
    target_server: str
    """대상 서버 주소"""
    target_port: int = 514
    """대상 포트 번호 (기본값: 514)"""
    protocol: str = "udp"
    """전송 프로토콜 (기본값: udp)"""


class SyslogResponse(BaseModel):
    """Syslog 응답 데이터 구조를 정의하는 클래스입니다."""

    success: bool
    """처리 성공 여부를 나타내는 boolean 값입니다."""

    parsed_message: Optional[Union[SyslogMessage, RFC5424SyslogMessage]] = None
    """파싱된 syslog 메시지 객체입니다. 파싱에 실패한 경우 None입니다."""

    error: Optional[str] = None
    """처리 중 발생한 오류 메시지입니다. 성공적인 처리인 경우 None입니다."""

    sent_to: Optional[str] = None
    """메시지가 전송된 대상입니다. 전송되지 않은 경우 None입니다."""

    generated_message: Optional[str] = None
    """생성된 syslog 메시지 문자열입니다. 생성되지 않은 경우 None입니다."""
