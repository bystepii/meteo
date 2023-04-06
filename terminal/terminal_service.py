import logging

from common.log import format_proto_msg
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData
from proto.services.terminal.terminal_service_pb2 import Results

logger = logging.getLogger(__name__)


class TerminalService:
    def __init__(self):
        logger.info("Initializing TerminalService")

    def receive_results(self, results: Results):
        logger.info(f"Received results: {format_proto_msg(results)}")
