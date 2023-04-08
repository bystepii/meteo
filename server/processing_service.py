import asyncio
import logging
from typing import Optional

from redis.asyncio import Redis

from common.log import format_proto_msg
from common.meteo_utils import MeteoDataProcessor
from common.store_strategy import StoreStrategy, SortedSetStoreStrategy
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(self, processor: MeteoDataProcessor, redis: Redis, store_strategy: Optional[StoreStrategy] = None):
        logger.info("Initializing ProcessingService")
        self._processor = processor
        self._store = store_strategy or SortedSetStoreStrategy(redis)

    async def process_meteo_data(self, raw_meteo_data: RawMeteoData):
        logger.debug(f"Processing raw meteo data {format_proto_msg(raw_meteo_data)}")
        loop = asyncio.get_running_loop()
        # run blocking code in a thread pool
        wellness_data = await loop.run_in_executor(None, self._processor.process_meteo_data, raw_meteo_data)
        # wellness_data = await asyncio.to_thread(self._processor.process_meteo_data, raw_meteo_data)
        logger.debug(f"Obtained wellness data \"{wellness_data}\"")
        if await self._store.store("wellness", raw_meteo_data.timestamp.ToNanoseconds(), wellness_data):
            logger.debug(f"Stored wellness data in redis")
        else:
            logger.warning(f"Failed to store wellness data \"{wellness_data}\"")

    async def process_pollution_data(self, raw_pollution_data: RawPollutionData):
        logger.debug(f"Processing raw pollution data {format_proto_msg(raw_pollution_data)}")
        loop = asyncio.get_running_loop()
        # run blocking code in a thread pool
        pollution_data = await loop.run_in_executor(None, self._processor.process_pollution_data, raw_pollution_data)
        # pollution_data = await asyncio.to_thread(self._processor.process_pollution_data, raw_pollution_data)
        logger.debug(f"Obtained pollution data \"{pollution_data}\"")
        if await self._store.store("pollution", raw_pollution_data.timestamp.ToNanoseconds(), pollution_data):
            logger.debug(f"Stored pollution data in redis")
        else:
            logger.warning(f"Failed to store pollution data \"{pollution_data}\"")
