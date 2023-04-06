import logging
import time
from typing import Tuple, Optional

import grpc
from redis import Redis

from common.observer import Observer, Observable
from common.registration_service import RegistrationService
from proto.services.terminal.terminal_service_pb2 import Results

logger = logging.getLogger(__name__)

DEFAULT_WINDOW_INTERVAL = 2000


class TumblingWindow(Observer):
    def __init__(
            self,
            registration_service: RegistrationService,
            redis: Redis,
            window_interval: Optional[int] = None,
    ):
        logger.info(f"Creating TumblingWindow with window interval {window_interval}")
        self._registration_service = registration_service
        self._window_interval = window_interval or DEFAULT_WINDOW_INTERVAL
        self._redis = redis
        self._channels = {}
        self._registration_service.attach(self)

    def update(self, subject: RegistrationService):
        addresses = list(subject.get_addresses())
        logger.debug(f"LoadBalancer received update from {subject} with addresses {addresses}")
        self._channels = {address: grpc.insecure_channel(str(address)) for address in addresses}

    def run(self):
        last_time = time.time()
        while True:
            time.sleep(self._window_interval / 1000)
            end = last_time + self._window_interval / 1000
            assert end <= time.time()
            logger.debug(f"Running tumbling window from {last_time} to {end}")
            results = Results()
            results.wellness_data, wellness_timestamp = self._get_data("wellness", last_time, end)
            results.wellness_timestamp.FromNanoseconds(int(wellness_timestamp * 1e9))
            results.pollution_data, pollution_timestamp = self._get_data("pollution", last_time, end)
            results.pollution_timestamp.FromNanoseconds(int(pollution_timestamp * 1e9))
            last_time = end
            self.notify(results)

    def notify(self, results: Results):
        for channel in self._channels.values():
            channel.stub.SendResults(results)

    def _get_data(self, key: str, start: float, end: float) -> Tuple[float, float]:
        res = self._redis.zrange(key, start=start, end=end, byscore=True, withscores=True)
        logger.debug(f"Got data from redis for key {key}: {res}")
        # returns a lis of tuples (key, score) where key is the value and score is the timestamp
        if not res or len(res) == 0:
            return 0, 0
        last_time = max(res, key=lambda x: x[1])[1]
        mean = sum([float(x[0]) for x in res]) / len(res)
        logger.debug(f"Computed mean {mean} for key {key} from {start} to {end} with last time {last_time}")
        return mean, last_time
