from typing import NoReturn
from typing import Optional

from fastapi import HTTPException
from starlette import status

from framework.config import settings


def check_password(password: str, detail: str) -> Optional[NoReturn]:
    if not password or password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
