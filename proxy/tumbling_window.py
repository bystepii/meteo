import asyncio
import logging
import time
from asyncio import Task
from typing import Tuple, Optional, Dict, List

import grpc.aio
from grpc.aio import Channel
from redis.asyncio import Redis

from common.observer import Observer
from common.registration_service import RegistrationService, Address
from common.store_strategy import StoreStrategy, SortedSetStoreStrategy
from proto.services.terminal.terminal_service_pb2 import Results
from proto.services.terminal.terminal_service_pb2_grpc import TerminalServiceStub

logger = logging.getLogger(__name__)

DEFAULT_WINDOW_INTERVAL = 2000
STARTUP_DELAY = 5


class TumblingWindow(Observer):
    def __init__(
            self,
            registration_service: RegistrationService,
            redis: Redis,
            default_window_interval: Optional[int] = None,
            store_strategy: Optional[StoreStrategy] = None,
    ):
        logger.info(f"Creating TumblingWindow with window interval {default_window_interval}")
        self._registration_service = registration_service
        self._default_window_interval = default_window_interval or DEFAULT_WINDOW_INTERVAL
        self._store = store_strategy or SortedSetStoreStrategy(redis)
        self._addresses: List[Address] = []
        self._channels: Dict[int, Dict[str, Channel]] = {}
        self._coroutines: Dict[int, Task] = {}
        self._registration_service.attach(self)
        # create default coroutine
        self._coroutines[self._default_window_interval] = asyncio.create_task(
            self._run(self._default_window_interval)
        )
        self._channels[self._default_window_interval] = {}

    def update(self, subject: RegistrationService):
        addresses = list(subject.get_addresses())
        logger.debug(f"LoadBalancer received update from {subject} with addresses {addresses}")

        # remove channels and coroutines for addresses that are no longer registered
        for interval, channels in self._channels.items():
            for address in self._addresses:
                if address not in addresses:
                    logger.debug(f"Removing channel for {address}")
                    del channels[address.address]
            if not channels and interval is not self._default_window_interval:
                logger.debug(f"Removing coroutine for interval {interval}")
                self._coroutines[interval].cancel()
                del self._coroutines[interval]

        # get the intervals requested by the terminals from the address additional info
        # those with no interval requested will get the default interval
        for address in addresses:
            try:
                interval = int(address.additional_info)
            except (TypeError, ValueError):
                interval = self._default_window_interval
            if interval not in self._channels:
                self._channels[interval] = {}
            if address.address not in self._channels[interval]:
                self._channels[interval][address.address] = grpc.aio.insecure_channel(
                    f"{address.address}:{address.port}"
                )

        # create a coroutine for each interval if it doesn't exist
        for interval, channels in self._channels.items():
            if interval not in self._coroutines:
                self._coroutines[interval] = asyncio.create_task(self._run(interval))

        self._addresses = addresses

    async def _run(self, interval: int):
        logger.debug(f"Starting tumbling window for interval {interval}")
        background_tasks = set()
        last_time = time.time()
        await asyncio.sleep(STARTUP_DELAY)
        while True:
            await asyncio.sleep(interval / 1000)
            end = last_time + interval / 1000
            assert end <= time.time()
            logger.debug(f"Running tumbling window from {last_time} to {end}")
            results = Results()
            (wellness_data, wellness_timestamp), (pollution_data, pollution_timestamp) = await asyncio.gather(
                self._get_data("wellness", last_time, end),
                self._get_data("pollution", last_time, end),
            )
            results.wellness_data = wellness_data
            results.wellness_timestamp.FromNanoseconds(int(wellness_timestamp * 1e9))
            results.pollution_data = pollution_data
            results.pollution_timestamp.FromNanoseconds(int(pollution_timestamp * 1e9))
            last_time = end
            task = asyncio.create_task(self._send_results(results, interval))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

    async def _send_results(self, results: Results, interval: int):
        logger.debug(f"Sending results to terminals with interval {interval}")
        for address, channel in self._channels[interval].items():
            logger.debug(f"Sending results to {address}")
            stub = TerminalServiceStub(channel)
            await stub.SendResults(results)

    async def _get_data(self, key: str, start: float, end: float) -> Tuple[float, float]:
        res = await self._store.get(key, start, end)
        logger.debug(f"Got data from redis for key {key}: {res}")
        # returns a lis of tuples (key, score) where key is the value and score is the timestamp
        if not res or len(res) == 0:
            return 0, 0
        last_time = max(res, key=lambda x: x[1])[1]
        mean = sum([float(x[0]) for x in res]) / len(res)
        logger.debug(f"Computed mean {mean} for key {key} from {start} to {end} with last time {last_time}")
        return mean, last_time
