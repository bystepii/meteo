import asyncio
import logging
import time
from typing import Tuple, Optional, Dict

import grpc
from redis.asyncio import Redis

from common.observer import Observer
from common.registration_service import RegistrationService
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
        self._channels: Dict[int, Dict[str, grpc.Channel]] = {}
        self._coroutines: Dict[int, asyncio.Task] = {}
        self._registration_service.attach(self)

    def update(self, subject: RegistrationService):
        addresses = list(subject.get_addresses())
        logger.debug(f"LoadBalancer received update from {subject} with addresses {addresses}")

        # cancel all coroutines
        for interval, coroutine in self._coroutines.items():
            coroutine.cancel()
        self._coroutines = {}

        # close all channels
        for channels in self._channels.values():
            for channel in channels.values():
                channel.close()
        self._channels = {}

        # get the intervals requested by the terminals from the address additional info
        # those with no interval requested will get the default interval
        for address in addresses:
            try:
                interval = int(address.additional_info)
            except (TypeError, ValueError):
                interval = self._default_window_interval
            if interval not in self._channels:
                self._channels[interval] = {}
            self._channels[interval][address.address] = grpc.insecure_channel(
                f"{address.address}:{address.port}"
            )

        # create a coroutine for each interval if it doesn't exist
        for interval, channels in self._channels.items():
            if interval not in self._coroutines:
                self._coroutines[interval] = asyncio.create_task(self._run(interval))

    async def _run(self, interval: int):
        logger.debug(f"Starting tumbling window for interval {interval}")
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
            await self._send_results(results, interval)

    async def _send_results(self, results: Results, interval: int):
        logger.debug(f"Sending results to terminals with interval {interval}")
        for address, channel in self._channels[interval].items():
            logger.debug(f"Sending results to {address}")
            stub = TerminalServiceStub(channel)
            stub.SendResults.future(results)

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
