from typing import Any
from fastapi.responses import JSONResponse

def SuccessResponse(status_code: int, message: dict[str, Any]):
    return JSONResponse(
        status_code=status_code,
        content=message
    )