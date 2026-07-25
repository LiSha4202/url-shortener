from fastapi import HTTPException, status


def exc_401_not_val_cred(header_type: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials [ID-1]",
        headers={"WWW-Authentificate": header_type},
    )


def exc_link_404_not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Link not found or not belong to user [ID-2]",
    )


def exc_link_410_gone():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Link expired [ID-3]",
    )


def exc_log_click_500_server_error():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to log click [ID-4]",
    )


def exc_short_code_existing(shortcode: str):
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Short code '{shortcode}' is already in use [ID-5]",
    )


def exc_400_expires_not_provided():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Expires at must be provided [ID-6]",
    )


def exc_401_user_not_auth():
    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="Not Authentificated [ID-7]",
    )


def exc_403_user_forbidden_to_link():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Link does not belong to the current user [ID-8]",
    )
