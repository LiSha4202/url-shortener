from fastapi import HTTPException, status


def get_401_exception(header_type: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authentificate": header_type},
    )


def exc_link_404_not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Link not found",
    )


def exc_link_410_gone():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Link expired",
    )


def exc_log_click_500_server_error():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to log click",
    )


def exc_short_code_existing(shortcode: str):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Short code '{shortcode}' is already in use",
    )
