from datetime import datetime
from fastapi import Request, Response

async def add_process_time_header(request: Request, call_next):
    "Middleware to add X-Process-Time header"
    start_time = datetime.utcnow()
    response: Response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response