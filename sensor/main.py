import logging
import os
import random
import uuid
from typing import Optional

import click
import grpc

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.meteo_utils import MeteoDataDetector
from proto.services.meteo.meteo_service_pb2_grpc import MeteoServiceStub
from sensor import SensorType, create_sensor

logger = logging.getLogger(__name__)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('meteo-service-address', type=str, required=False, default=os.environ.get('METEO_SERVICE_ADDRESS'))
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default=os.environ.get("LOG_LEVEL", "info"), help="Set the log level")
@click.option('--sensor-id', type=str, default=uuid.uuid4().hex, help="Set the sensor id")
@click.option('--sensor-type', type=click.Choice([e.value for e in SensorType]),
              default=random.choice(list(SensorType)).value, help="Set the sensor type")
@click.option('--interval', type=int, help="Set the sensor interval in ms")
def main(
        meteo_service_address: str,
        sensor_id: str,
        sensor_type: str,
        debug: bool = False,
        log_level: str = 'info',
        interval: Optional[int] = None
):
    setup_logger(log_level=logging.DEBUG if debug else log_level.upper())

    if not meteo_service_address:
        raise ValueError("Meteo service address not provided")

    logger.info(f"Starting sensor {sensor_id} of type {sensor_type}")

    meteo = MeteoServiceStub(grpc.insecure_channel(meteo_service_address))

    sensor = create_sensor(sensor_id, MeteoDataDetector(), meteo, SensorType(sensor_type), interval)

    logger.info("Starting sensor loop")

    try:
        sensor.run()
    except KeyboardInterrupt:
        logger.info("Shutting down sensor")


if __name__ == '__main__':
    setup_logger()
    main()
