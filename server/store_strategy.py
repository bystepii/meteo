from abc import abstractmethod, ABC
from typing import Any

from redis.asyncio import Redis


class StoreStrategy(ABC):
    @abstractmethod
    async def store(self, key: str, timestamp_ns: int, value: Any) -> None:
        pass


class SortedSetStoreStrategy(StoreStrategy):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def store(self, key: str, timestamp_ns: int, value: Any):
        await self._redis.zadd(key, {value: timestamp_ns / 1e9})


class TimeSeriesStoreStrategy(StoreStrategy):
    def __init__(self, redis: Redis):
        self._ts = redis.ts()

    async def store(self, key: str, timestamp_ns: int, value: Any):
        self._ts.add(key, int(timestamp_ns / 1e6), value)
