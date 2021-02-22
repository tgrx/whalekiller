from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from main.actions import update_timings


class BenchMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        t0 = datetime.utcnow()
        try:
            response = await call_next(request)
        finally:
            t = datetime.utcnow()
            delta = (t - t0).total_seconds()

            update_timings(request.url.path, delta)

        return response
