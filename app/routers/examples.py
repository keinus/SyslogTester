"""
예제 관리 API 라우터

이 모듈은 예제 생성, 조회, 수정, 삭제 기능을 제공하는 FastAPI 라우터입니다.
예제는 이름, 설명, RFC 버전, 원본 메시지로 구성되며,
데이터베이스와 연동하여 CRUD 작업을 처리합니다.
"""
from sqlite3 import (DataError, IntegrityError, OperationalError,
                     ProgrammingError)
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.core.database import example_db
from app.models.example import (CreateExampleRequest, ExampleResponse,
                                UpdateExampleRequest)


EXAMPLE_NOT_FOUND_MSG = "Example not found"

router = APIRouter(prefix="/api/examples", tags=["examples"])
"""예제 API 라우터 인스턴스"""


@router.post("/", response_model=ExampleResponse)
async def create_example(request: CreateExampleRequest) -> ExampleResponse:
    """예시를 생성하는 함수

    이 함수는 요청된 정보를 기반으로 새로운 예시를 데이터베이스에 생성합니다. 
    생성 중 발생할 수 있는 예외를 처리하여 적절한 응답을 반환합니다.

    Args:
        request (CreateExampleRequest): 생성할 예시의 정보를 담은 요청 객체

    Returns:
        ExampleResponse: 예시 생성 결과와 생성된 예시 데이터 또는 에러 메시지를 담은 응답 객체
    """
    try:
        example = example_db.create_example(
            name=request.name,
            description=request.description,
            rfc_version=request.rfc_version,
            raw_message=request.raw_message
        )
        return ExampleResponse(success=True, example=example)
    except (IntegrityError, DataError, OperationalError, ProgrammingError) as e:
        return ExampleResponse(success=False, error=str(e))


@router.get("/", response_model=ExampleResponse)
async def get_examples(rfc_version: Optional[str] = None) -> ExampleResponse:
    """예시 목록을 반환

    RFC 버전에 따라 예시 데이터를 조회하며, 버전이 지정되지 않은 경우 모든 예시를 반환합니다.
    데이터베이스 오류가 발생하면 실패 응답을 반환합니다.

    Args:
        rfc_version (Optional[str], optional): 조회할 RFC 버전. Defaults to None.

    Returns:
        ExampleResponse: 예시 목록 또는 오류 정보를 포함한 응답 객체
    """
    try:
        examples = example_db.get_examples(rfc_version=rfc_version)
        return ExampleResponse(success=True, examples=examples)
    except (DataError, IntegrityError, OperationalError, ProgrammingError) as e:
        return ExampleResponse(success=False, error=str(e))


@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(example_id: int) -> ExampleResponse:
    """예시 항목을 조회합니다.

    주어진 ID에 해당하는 예시 항목을 데이터베이스에서 검색합니다. 
    항목이 존재하지 않을 경우 404 오류를 반환합니다. 
    데이터베이스 관련 예외가 발생한 경우 실패 응답을 반환합니다.
    
    Args:
        example_id (int): 조회할 예시 항목의 고유 ID

    Raises:
        HTTPException: 항목이 존재하지 않을 경우 404 오류 발생

    Returns:
        ExampleResponse: 조회 결과를 포함한 응답 객체
    """
    try:
        example = example_db.get_example(example_id)
        if not example:
            raise HTTPException(status_code=404, detail=EXAMPLE_NOT_FOUND_MSG)
        return ExampleResponse(success=True, example=example)
    except (DataError, IntegrityError, OperationalError, ProgrammingError) as e:
        return ExampleResponse(success=False, error=str(e))


@router.put("/{example_id}", response_model=ExampleResponse)
async def update_example(example_id: int, request: UpdateExampleRequest) -> ExampleResponse:
    """예시 항목 수정

    예시 항목의 정보를 수정하여 데이터베이스에 반영한다. 만약 해당 ID의 예시가 존재하지 않으면 404 오류를 반환한다.
    데이터베이스 작업 중 발생할 수 있는 다양한 예외들을 처리하여 적절한 응답을 반환한다.

    Args:
        example_id (int): 업데이트할 예시 항목의 고유 ID
        request (UpdateExampleRequest): 업데이트할 예시 항목의 정보를 담은 요청 객체

    Raises:
        HTTPException: 예시 항목이 존재하지 않을 경우 404 오류 발생

    Returns:
        ExampleResponse: 업데이트 결과와 예시 항목 정보를 담은 응답 객체
    """
    try:
        example = example_db.update_example(
            example_id=example_id,
            name=request.name,
            description=request.description,
            rfc_version=request.rfc_version,
            raw_message=request.raw_message
        )
        if not example:
            raise HTTPException(status_code=404, detail=EXAMPLE_NOT_FOUND_MSG)
        return ExampleResponse(success=True, example=example)
    except (DataError, IntegrityError, OperationalError, ProgrammingError) as e:
        return ExampleResponse(success=False, error=str(e))


@router.delete("/{example_id}", response_model=ExampleResponse)
async def delete_example(example_id: int) -> ExampleResponse:
    """예제 삭제

    예제 ID에 해당하는 데이터를 데이터베이스에서 삭제합니다. 삭제 중 문제가 발생하면 예외를 발생시킵니다.
    데이터베이스 작업 중 오류가 발생하면 그에 대한 정보를 포함한 응답을 반환합니다.

    Args:
        example_id (int): 삭제할 예제의 고유 ID

    Raises:
        HTTPException: 예제가 존재하지 않을 경우 404 상태 코드와 함께 발생

    Returns:
        ExampleResponse: 삭제 성공 여부와 오류 메시지를 포함한 응답
    """
    try:
        success = example_db.delete_example(example_id)
        if not success:
            raise HTTPException(status_code=404, detail=EXAMPLE_NOT_FOUND_MSG)
        return ExampleResponse(success=True)
    except (DataError, IntegrityError, OperationalError, ProgrammingError) as e:
        return ExampleResponse(success=False, error=str(e))
