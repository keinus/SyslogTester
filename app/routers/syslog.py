"""
Syslog 처리를 위한 API 라우터 모듈

이 모듈은 syslog 메시지의 파싱, 생성, 전송 기능을 제공하며,
RFC 3164와 RFC 5424 형식을 지원한다.
"""
from typing import Any
from fastapi import APIRouter, Form
from app.models import (
    SyslogRequest,
    GenerateRequest,
    MessageComponents,
    SyslogResponse,
    SyslogMessage,
)

from app.parsers import parse_service
from app.generators import generator_service
from app.senders import SyslogSender


router = APIRouter(prefix="/api/syslog", tags=["syslog"])
"""API 라우터를 설정"""


@router.post("/parse", response_model=SyslogResponse)
async def parse_syslog(request: SyslogRequest) -> SyslogResponse:
    """syslog 메시지를 파싱 및 전송

    요청된 RFC 버전에 따라 적절한 파서를 선택하여 syslog 메시지를 파싱합니다. 
    파싱이 성공적으로 완료되면 지정된 프로토콜(UDP 또는 TCP)을 사용하여 메시지를 전송합니다.
    전송 실패 시 예외 처리를 통해 오류 정보를 반환합니다.

    Args:
        request (SyslogRequest): syslog 파싱 및 전송에 필요한 요청 데이터

    Raises:
        ValueError: 지원되지 않는 프로토콜 또는 파싱 중 발생한 유효성 오류

    Returns:
        SyslogResponse: 파싱 결과와 전송 상태를 포함하는 응답
    """
    print(f"Received request: {request}")

    try:
        parsed_message: SyslogMessage = parse_service.parse(
            request.rfc_version, request.raw_message
        )

        await SyslogSender.send(
            request.protocol.lower(), request.raw_message,
            request.target_server, request.target_port
        )

        response = SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            sent_to=f"{request.target_server}:{request.target_port} ({request.protocol.upper()})"
        )

        print(f"Response: {response}")
        return response

    except ValueError as e:
        print(f"Validation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )
    except ConnectionError as e:
        print(f"Transmission error: {e}")
        return SyslogResponse(
            success=False,
            error=f"Transmission error: {str(e)}"
        )


@router.post("/parse-only", response_model=SyslogResponse)
async def parse_only(raw_message: str = Form(...),
                     rfc_version: str = Form("3164")) -> SyslogResponse:
    """로그 메시지를 파싱

    로우 메시지와 RFC 버전을 입력받아 해당 형식에 맞춰서 파싱합니다. 지원하는 RFC 버전은 3164와 5424입니다.
    파싱이 성공하면 파싱된 메시지를 반환하고 실패하면 에러 메시지를 반환합니다.

    Args:
        raw_message (str, optional): 파싱할 원시 로그 메시지입니다. Defaults to Form(...).
        rfc_version (str, optional): 사용할 RFC 버전입니다. Defaults to Form("3164").

    Returns:
        SyslogResponse: 파싱 성공 여부와 결과를 포함한 응답 객체입니다.
    """
    print(f"Parse-only request: {raw_message}, RFC: {rfc_version}")

    try:
        # Select parser based on RFC version
        parsed_message: SyslogMessage = parse_service.parse(
            rfc_version, raw_message
        )

        return SyslogResponse(
            success=True,
            parsed_message=parsed_message
        )

    except ValueError as e:
        print(f"Parse-only error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )


@router.post("/generate", response_model=SyslogResponse)
async def generate_syslog(request: GenerateRequest) -> SyslogResponse:
    """시스템 로그 메시지를 생성하고 전송하며, 결과를 반환

    요청된 구성 요소와 프로토콜에 따라 시스템 로그 메시지를 생성하고 지정된 서버로 전송한다
    전송 후 생성된 메시지를 파싱하여 구조화된 데이터로 반환한다
    오류가 발생하면 실패 응답을 반환한다

    Args:
        request (GenerateRequest): 로그 생성 요청 정보를 포함하는 객체

    Returns:
        SyslogResponse: 생성 성공 여부, 파싱된 메시지, 생성된 메시지, 전송 정보를 포함한 응답
    """
    print(f"Generate request: {request}")

    try:
        generated_message = generator_service.generate(
            request.components.rfc_version, request.components
        )

        await SyslogSender.send(
            request.protocol.lower(), generated_message,
            request.target_server, request.target_port
        )

        # Parse the generated message to return structured data
        parsed_message: SyslogMessage = parse_service.parse(
            request.components.rfc_version, generated_message
        )

        response = SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            generated_message=generated_message,
            sent_to=f"{request.target_server}:{request.target_port} ({request.protocol.upper()})"
        )

        print(f"Response: {response}")
        return response

    except ValueError as e:
        print(f"Generation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )
    except ConnectionError as e:
        print(f"Transmission error: {e}")
        return SyslogResponse(
            success=False,
            error=f"Transmission error: {str(e)}"
        )


@router.post("/generate-only", response_model=SyslogResponse)
async def generate_only(components: MessageComponents) -> SyslogResponse:
    """생성 전용 syslog 메시지 생성 및 파싱

    주어진 메시지 구성 요소를 사용하여 syslog 메시지를 생성하고 파싱합니다. 
    생성된 메시지는 RFC 버전에 따라 형식화되며, 파싱 결과는 응답으로 반환됩니다.
    오류가 발생하면 실패 응답과 함께 에러 메시지를 반환합니다.

    Args:
        components (MessageComponents): syslog 메시지 생성에 필요한 구성 요소들

    Returns:
        SyslogResponse: 생성 성공 여부와 결과 메시지 또는 에러 정보
    """
    print(f"Generate-only request: {components}")

    try:
        generated_message = generator_service.generate(
            components.rfc_version, components
        )
        parsed_message: SyslogMessage = parse_service.parse(
            components.rfc_version, generated_message
        )

        return SyslogResponse(
            success=True,
            parsed_message=parsed_message,
            generated_message=generated_message
        )

    except ValueError as e:
        print(f"Generation error: {e}")
        return SyslogResponse(
            success=False,
            error=str(e)
        )


@router.get("/validate/{message}/{rfc_version}")
async def validate_format(message: str, rfc_version: str = "3164") -> dict[str, Any]:
    """RFC 형식에 따라 시스템 로그 메시지를 검증하고 파싱

    메시지와 RFC 버전을 기반으로 시스템 로그 포맷의 유효성을 검사하며,
    유효한 경우 파싱된 결과를 반환하고, 유효하지 않은 경우 오류 메시지를 반환합니다.
    지원되는 RFC 버전은 3164와 5424입니다.

    Args:
        message: 검증할 시스템 로그 메시지 문자열
        rfc_version: 사용할 RFC 형식 버전 (기본값은 "3164")

    Returns:
        유효성 검사 결과와 파싱된 메시지 또는 오류 정보를 포함하는 딕셔너리
    """
    try:
        # Select parser based on RFC version
        parsed_message: SyslogMessage = parse_service.parse(
            rfc_version, message
        )

        return {
            "valid": True,
            "parsed": parsed_message.model_dump(),
            "rfc_version": rfc_version
        }
    except ValueError as e:
        return {
            "valid": False,
            "error": str(e),
            "rfc_version": rfc_version
        }
