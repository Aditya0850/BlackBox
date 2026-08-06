"""Redis queue client for pipeline job processing."""
import json
import logging
from typing import Any, Optional, Callable, Awaitable
from uuid import UUID

import redis.asyncio as redis

from ...config import get_settings

logger = logging.getLogger(__name__)


class RedisQueueClient:
    """Client for Redis queue operations."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        password: Optional[str] = None,
    ):
        settings = get_settings()
        self.host = host or settings.REDIS_HOST
        self.port = port or settings.REDIS_PORT
        self.db = db
        self.password = password

        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
            )
            await self._client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Redis")

    async def _ensure_connected(self) -> redis.Redis:
        """Ensure connection is established and return client."""
        if self._client is None:
            await self.connect()
        return self._client

    # Queue operations
    async def enqueue(self, queue_name: str, payload: dict[str, Any]) -> bool:
        """Add a job to the queue."""
        try:
            client = await self._ensure_connected()
            await client.lpush(queue_name, json.dumps(payload))
            logger.debug(f"Enqueued job to {queue_name}: {payload}")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            return False

    async def dequeue(
        self, queue_name: str, timeout: int = 5
    ) -> Optional[dict[str, Any]]:
        """Remove and return a job from the queue (blocking)."""
        try:
            client = await self._ensure_connected()
            result = await client.brpop(queue_name, timeout=timeout)
            if result:
                _, payload = result
                return json.loads(payload)
            return None
        except Exception as e:
            logger.error(f"Failed to dequeue job: {e}")
            return None

    async def queue_length(self, queue_name: str) -> int:
        """Get the length of a queue."""
        try:
            client = await self._ensure_connected()
            return await client.llen(queue_name)
        except Exception as e:
            logger.error(f"Failed to get queue length: {e}")
            return 0

    # Pub/Sub for real-time updates
    async def publish(self, channel: str, message: dict[str, Any]) -> int:
        """Publish a message to a channel."""
        try:
            client = await self._ensure_connected()
            return await client.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return 0

    async def subscribe(
        self, channel: str, handler: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Subscribe to a channel and handle messages."""
        try:
            client = await self._ensure_connected()
            pubsub = client.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"Subscribed to channel: {channel}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        payload = json.loads(message["data"])
                        await handler(payload)
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")

    # Cache operations (for temporary data)
    async def set_cache(
        self, key: str, value: Any, ttl: int = 3600
    ) -> bool:
        """Set a cache value with TTL."""
        try:
            client = await self._ensure_connected()
            await client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False

    async def get_cache(self, key: str) -> Optional[Any]:
        """Get a cache value."""
        try:
            client = await self._ensure_connected()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None

    async def delete_cache(self, key: str) -> bool:
        """Delete a cache value."""
        try:
            client = await self._ensure_connected()
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False


# Module-level client instance
_redis_queue: Optional[RedisQueueClient] = None


def get_redis_queue() -> RedisQueueClient:
    """Get the singleton Redis queue client instance."""
    global _redis_queue
    if _redis_queue is None:
        _redis_queue = RedisQueueClient()
    return _redis_queue