from fastapi import HTTPException, status


def network_exception():
    return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, 
            detail="Network took too long to respond. Please try again later", 
        )