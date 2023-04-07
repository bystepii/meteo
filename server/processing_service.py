import logging
from typing import Optional

from redis import Redis

from common.log import format_proto_msg
from common.meteo_utils import MeteoDataProcessor
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData
from server.store_strategy import StoreStrategy, SortedSetStoreStrategy

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(self, processor: MeteoDataProcessor, redis: Redis, store_strategy: Optional[StoreStrategy] = None):
        logger.info("Initializing ProcessingService")
        self._processor = processor
        self._store = store_strategy or SortedSetStoreStrategy(redis)

    def process_meteo_data(self, raw_meteo_data: RawMeteoData):
        logger.debug(f"Processing raw meteo data {format_proto_msg(raw_meteo_data)}")
        wellness_data = self._processor.process_meteo_data(raw_meteo_data)
        logger.debug(f"Obtained wellness data \"{wellness_data}\"")
        self._store.store("wellness", raw_meteo_data.timestamp.ToNanoseconds(), wellness_data)
        return wellness_data

    def process_pollution_data(self, raw_pollution_data: RawPollutionData):
        logger.debug(f"Processing raw pollution data {format_proto_msg(raw_pollution_data)}")
        pollution_data = self._processor.process_pollution_data(raw_pollution_data)
        logger.debug(f"Obtained pollution data \"{pollution_data}\"")
        self._store.store("pollution", raw_pollution_data.timestamp.ToNanoseconds(), pollution_data)
        return pollution_data
