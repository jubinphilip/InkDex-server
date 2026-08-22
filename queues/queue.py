import os

from dotenv import load_dotenv
from redis import Redis
from rq import Queue

load_dotenv()

redis_connection = Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

document_queue = Queue(
    "documents",
    connection=redis_connection
)
