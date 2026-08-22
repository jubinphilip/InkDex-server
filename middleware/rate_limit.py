import time

from fastapi import Request, HTTPException, status

from queues.queue import redis_connection


MAX_REQUESTS = 10
WINDOW_SECONDS = 60


async def rate_limit(request: Request):

    client_ip = request.client.host

    current_window = int(
        time.time() // WINDOW_SECONDS
    )

    key = f"rate_limit:{client_ip}:{current_window}"

    current_count = redis_connection.get(key)

    if current_count is None:

        redis_connection.set(
            key,
            1,
            ex=WINDOW_SECONDS
        )

    else:

        current_count = int(current_count)

        if current_count >= MAX_REQUESTS:

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )

        redis_connection.incr(key)