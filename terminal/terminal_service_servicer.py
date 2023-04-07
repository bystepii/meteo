import asyncio
import logging

from google.protobuf.empty_pb2 import Empty
from grpc import ServicerContext

from proto.services.terminal import terminal_service_pb2_grpc
from proto.services.terminal.terminal_service_pb2 import Results
from terminal_service import TerminalService

logger = logging.getLogger(__name__)


class TerminalServiceServicer(terminal_service_pb2_grpc.TerminalServiceServicer):
    def __init__(self, terminal_service: TerminalService):
        logger.info("Initializing TerminalServiceServicer")
        self._terminal_service = terminal_service

    async def SendResults(self, results: Results, context: ServicerContext) -> Empty:
        logger.info(f"{context.peer()} called SendResults")
        asyncio.create_task(self._terminal_service.receive_results(results))
        return Empty()
