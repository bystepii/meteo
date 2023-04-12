import asyncio
import logging
import os
import random
import signal
import uuid
from typing import Optional

import asyncclick as click
import grpc.aio

from common.log import setup_logger, LOGGER_LEVEL_CHOICES
from common.meteo_utils import MeteoDataDetector
from proto.services.meteo.meteo_service_pb2_grpc import MeteoServiceStub
from sensor import SensorType, create_sensor

logger = logging.getLogger(__name__)

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('meteo-service-address', type=str, required=False, default=os.environ.get('METEO_SERVICE_ADDRESS'))
@click.option('--debug', is_flag=True, help="Enable debug logging")
@click.option('--log-level', type=click.Choice(LOGGER_LEVEL_CHOICES),
              default=os.environ.get("LOG_LEVEL", "info"), help="Set the log level")
@click.option('--sensor-id', type=str, default=uuid.uuid4().hex, help="Set the sensor id")
@click.option('--sensor-type', type=click.Choice([e.value for e in SensorType]),
              default=os.environ.get("SENSOR_TYPE", random.choice(list(SensorType)).value), help="Set the sensor type")
@click.option('--interval', type=int, default=os.environ.get("INTERVAL"), help="Set the sensor interval in ms")
async def main(
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

    meteo = MeteoServiceStub(grpc.aio.insecure_channel(meteo_service_address))

    sensor = create_sensor(sensor_id, MeteoDataDetector(), meteo, SensorType(sensor_type), interval)

    logger.info("Starting sensor loop")

    try:
        await sensor.run()
    except asyncio.CancelledError:
        logger.info("Shutting down sensor")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    async def _finish():
        logger.info("Shutting down")
        await asyncio.gather(*_cleanup_coroutines, return_exceptions=True)
        tasks = asyncio.all_tasks() - {asyncio.current_task()}
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Shutting down asyncio loop")
        loop.stop()
        loop.close()
        exit(0)


    background_tasks = set()


    def signal_handler(sig):
        logger.info(f"Received signal {sig}")
        task = asyncio.create_task(_finish())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)


    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda: signal_handler(s))

    try:
        loop.run_until_complete(main.main())
    finally:
        logger.info("Received keyboard interrupt, shutting down")
