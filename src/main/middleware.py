from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from framework.config import settings
from main.actions import update_timings


class BenchMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.BENCHMARK_REQUESTS:
            return await call_next(request)

        t0 = datetime.utcnow()
        try:
            response = await call_next(request)
        finally:
            t = datetime.utcnow()
            delta = (t - t0).total_seconds()

            update_timings(request.url.path, delta)

        return response
