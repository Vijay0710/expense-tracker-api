from fastapi import HTTPException, status


def current_user_exception():
    return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Couldn't validate credentials", 
            headers={"WWW-Authenticate" : "Bearer"}
        )