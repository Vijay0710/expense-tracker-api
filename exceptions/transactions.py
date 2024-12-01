from fastapi import HTTPException, status


def not_found_exception(message: str = "Transaction not found"):
    return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=message
        )