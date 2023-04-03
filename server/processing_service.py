import logging

from redis import Redis

from common.log import format_proto_msg
from common.meteo_utils import MeteoDataProcessor
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(self, processor: MeteoDataProcessor, redis: Redis):
        logger.info("Initializing MeteoService")
        self._processor = processor
        self._redis = redis

    def process_meteo_data(self, meteo_data: RawMeteoData):
        logger.debug(f"Processing meteo data {format_proto_msg(meteo_data)}")
        wellness_data = self._processor.process_meteo_data(meteo_data)
        logger.debug(f"Obtained wellness data \"{wellness_data}\"")
        self._redis.zadd("wellness", {RawMeteoData.timestamp.ToNanoseconds() / 1e9: wellness_data})
        return wellness_data

    def process_pollution_data(self, pollution_data: RawPollutionData):
        logger.debug(f"Processing pollution data {format_proto_msg(pollution_data)}")
        pollution_data = self._processor.process_pollution_data(pollution_data)
        logger.debug(f"Obtained pollution data \"{pollution_data}\"")
        self._redis.zadd("pollution", {RawPollutionData.timestamp.ToNanoseconds() / 1e9: pollution_data})
        return pollution_data
