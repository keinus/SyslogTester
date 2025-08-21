from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.example import CustomExample, CreateExampleRequest, UpdateExampleRequest, ExampleResponse
from app.core.database import example_db

router = APIRouter(prefix="/api/examples", tags=["examples"])


@router.post("/", response_model=ExampleResponse)
async def create_example(request: CreateExampleRequest):
    """Create a new custom example"""
    try:
        example = example_db.create_example(
            name=request.name,
            description=request.description,
            rfc_version=request.rfc_version,
            raw_message=request.raw_message
        )
        return ExampleResponse(success=True, example=example)
    except Exception as e:
        return ExampleResponse(success=False, error=str(e))


@router.get("/", response_model=ExampleResponse)
async def get_examples(rfc_version: Optional[str] = None):
    """Get all custom examples, optionally filtered by RFC version"""
    try:
        examples = example_db.get_examples(rfc_version=rfc_version)
        return ExampleResponse(success=True, examples=examples)
    except Exception as e:
        return ExampleResponse(success=False, error=str(e))


@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(example_id: int):
    """Get a specific example by ID"""
    try:
        example = example_db.get_example(example_id)
        if not example:
            raise HTTPException(status_code=404, detail="Example not found")
        return ExampleResponse(success=True, example=example)
    except HTTPException:
        raise
    except Exception as e:
        return ExampleResponse(success=False, error=str(e))


@router.put("/{example_id}", response_model=ExampleResponse)
async def update_example(example_id: int, request: UpdateExampleRequest):
    """Update an existing example"""
    try:
        example = example_db.update_example(
            example_id=example_id,
            name=request.name,
            description=request.description,
            rfc_version=request.rfc_version,
            raw_message=request.raw_message
        )
        if not example:
            raise HTTPException(status_code=404, detail="Example not found")
        return ExampleResponse(success=True, example=example)
    except HTTPException:
        raise
    except Exception as e:
        return ExampleResponse(success=False, error=str(e))


@router.delete("/{example_id}", response_model=ExampleResponse)
async def delete_example(example_id: int):
    """Delete an example"""
    try:
        success = example_db.delete_example(example_id)
        if not success:
            raise HTTPException(status_code=404, detail="Example not found")
        return ExampleResponse(success=True)
    except HTTPException:
        raise
    except Exception as e:
        return ExampleResponse(success=False, error=str(e))