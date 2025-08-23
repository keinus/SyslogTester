"""
사용자 정의 예제 모델 및 요청/응답 데이터 클래스를 정의하는 모듈입니다.
이 모듈은 예제 데이터를 관리하기 위한 Pydantic 모델들을 제공합니다.
각 모델은 데이터 유효성 검사 및 타입 힌트를 제공합니다.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CustomExample(BaseModel):
    """CustomExample 모델은 RFC 형식의 로그 메시지를 저장하고 관리하는 데이터 구조"""

    id: Optional[int] = None
    """기본 키"""
    name: str
    """이름"""
    description: Optional[str] = None
    """설명"""
    rfc_version: str  # "3164" or "5424"
    """RFC 버전 (3164 또는 5424)"""
    raw_message: str
    """원시 로그 메시지"""
    created_at: Optional[datetime] = None
    """생성 일시"""
    updated_at: Optional[datetime] = None
    """수정 일시"""


class CreateExampleRequest(BaseModel):
    """예제 생성 요청 데이터 모델을 정의

    이 모델은 예제 생성에 필요한 기본 정보를 담고 있으며, 
    필수 필드는 name과 rfc_version이며, description과 raw_message는 선택적으로 제공된다.
    """
    name: str
    """예제 이름"""
    description: Optional[str] = None
    """예제 설명"""
    rfc_version: str
    """RFC 버전"""
    raw_message: str
    """원본 메시지 내용"""


class UpdateExampleRequest(BaseModel):
    """업데이트 요청 데이터 모델을 정의한다."""

    name: Optional[str] = None
    """이름 필드 - 선택사항으로, 업데이트할 이름을 포함한다."""
    description: Optional[str] = None
    """설명 필드 - 선택사항으로, 업데이트할 설명을 포함한다."""
    rfc_version: Optional[str] = None
    """RFC 버전 필드 - 선택사항으로, 업데이트할 RFC 버전을 포함한다."""
    raw_message: Optional[str] = None
    """원시 메시지 필드 - 선택사항으로, 업데이트할 원시 메시지를 포함한다."""


class ExampleResponse(BaseModel):
    """예제 응답 모델을 정의한다."""

    success: bool
    """요청 성공 여부를 나타낸다."""
    example: Optional[CustomExample] = None
    """단일 예제 객체를 포함한다."""
    examples: Optional[List[CustomExample]] = None
    """예제 객체 리스트를 포함한다."""
    error: Optional[str] = None
    """에러 메시지를 포함한다."""
