from fastapi import HTTPException, status


def not_found_exception():
    return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Transaction not found"
        )