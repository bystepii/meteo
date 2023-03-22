import logging
import random

import click
import grpc

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from proto.services.meteo.meteo_service_pb2_grpc import MeteoServiceStub
from sensor.sensor import SensorType, create_sensor

logger = logging.getLogger(__name__)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('load_balancer_address', type=str, required=True, help="Set the load balancer address")
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default='info', help="Set the log level")
@click.option('--sensor-id', type=str, help="Set the sensor id")
@click.option('--sensor-type', type=click.Choice([s.value for s in SensorType]),
              default=random.choice(list(SensorType)).value, help="Set the sensor type")
def main(
        load_balancer_address: str,
        debug: bool = False,
        log_level: str = 'info',
        sensor_id: str = None,
        sensor_type: SensorType = None
):
    setup_logger(log_level=logging.DEBUG if debug else log_level.upper())

    logger.info(f"Starting sensor {sensor_id} of type {sensor_type}")

    meteo = MeteoServiceStub(grpc.insecure_channel(load_balancer_address))

    sensor = create_sensor(sensor_id, sensor_type, meteo)

    logger.info("Starting sensor loop")

    try:
        sensor.run()
    except KeyboardInterrupt:
        logger.info("Shutting down sensor")


if __name__ == '__main__':
    setup_logger()
    main()
