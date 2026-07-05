import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("app.middleware.logging")
logging.basicConfig(level=logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        # Log request basic info
        logger.info(f"Incoming Request: {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"Request Failed: {request.method} {request.url.path} - "
                f"Duration: {process_time:.4f}s - Error: {str(e)}"
            )
            raise e

        process_time = time.perf_counter() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {process_time:.4f}s"
        )
        return response
