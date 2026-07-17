from fastapi import HTTPException, status


def get_401_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authentificate": "Basic"},
    )
