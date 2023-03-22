from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from enum import Enum

from common.meteo_utils import MeteoDataDetector
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData
from proto.services.meteo.meteo_service_pb2_grpc import MeteoServiceStub

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL = 1


class SensorType(Enum):
    AirQuality = 'air_quality'
    Pollution = 'pollution'


class Sensor(ABC):
    def __init__(
            self, sensor_id: str,
            sensor_type: SensorType,
            meteo: MeteoServiceStub,
            interval: int = DEFAULT_INTERVAL
    ):
        self._sensor_id = sensor_id
        self._sensor_type = sensor_type
        self._meteo = meteo
        self._interval = interval
        self._detector = MeteoDataDetector()

    @property
    def sensor_id(self) -> str:
        return self._sensor_id

    @property
    def sensor_type(self) -> SensorType:
        return self._sensor_type

    @abstractmethod
    def get_data(self) -> RawMeteoData | RawPollutionData:
        pass

    @abstractmethod
    def send_data(self, data: RawMeteoData | RawPollutionData):
        pass

    def run(self):
        while True:
            time.sleep(self._interval)
            data = self.get_data()
            self.send_data(data)


class AirQualitySensor(Sensor):
    def __init__(self, sensor_id: str, meteo: MeteoServiceStub, interval: int = DEFAULT_INTERVAL):
        super().__init__(sensor_id, SensorType.AirQuality, meteo, interval)
        logger.info(f"Initializing AirQualitySensor {sensor_id} with interval {interval}")

    def get_data(self) -> RawMeteoData:
        data = RawMeteoData()
        air = self._detector.analyze_air()
        data.timestamp = time.time()
        data.humidity = air['humidity']
        data.temperature = air['temperature']
        logger.debug(f"Sensor {self._sensor_id} of type {self._sensor_type} generated data {data}")
        return data

    def send_data(self, data: RawMeteoData):
        logger.debug(f"Sensor {self._sensor_id} of type {self._sensor_type} sending data {data}")
        self._meteo.SendMeteoData(data)


class PollutionSensor(Sensor):
    def __init__(self, sensor_id: str, meteo: MeteoServiceStub, interval: int = DEFAULT_INTERVAL):
        super().__init__(sensor_id, SensorType.Pollution, meteo, interval)
        logger.info(f"Initializing PollutionSensor {sensor_id} with interval {interval}")

    def get_data(self) -> RawPollutionData:
        data = RawPollutionData()
        pollution = self._detector.analyze_pollution()
        data.timestamp = time.time()
        data.co2 = pollution['co2']
        logger.debug(f"Sensor {self._sensor_id} of type {self._sensor_type} generated data {data}")
        return data

    def send_data(self, data: RawPollutionData):
        logger.debug(f"Sensor {self._sensor_id} of type {self._sensor_type} sending data {data}")
        self._meteo.SendPollutionData(data)


def create_sensor(sensor_id: str, sensor_type: SensorType, meteo: MeteoServiceStub) -> Sensor:
    if sensor_type == SensorType.AirQuality:
        return AirQualitySensor(sensor_id, meteo)
    elif sensor_type == SensorType.Pollution:
        return PollutionSensor(sensor_id, meteo)
    else:
        raise ValueError(f"Invalid sensor type {sensor_type}")
