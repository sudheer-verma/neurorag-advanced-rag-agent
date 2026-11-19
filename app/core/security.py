from fastapi import HTTPException


def validate_identifier(value: str, field_name: str) -> str:
    value = value.strip()
    if not value:
        raise HTTPException(status_code=422, detail=f"{field_name} cannot be empty")
    if len(value) > 128:
        raise HTTPException(status_code=422, detail=f"{field_name} is too long")
    return value
