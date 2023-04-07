from __future__ import annotations

import logging
import random
from abc import ABC, abstractmethod
from typing import Sequence

import grpc.aio

from common.log import format_proto_msg
from common.observer import Observer
from common.registration_service import RegistrationService, Address
from proto.messages.meteo.meteo_messages_pb2 import RawMeteoData, RawPollutionData
from proto.services.processing.processing_service_pb2_grpc import ProcessingServiceStub

logger = logging.getLogger(__name__)


class LoadBalancer(Observer):
    """
    A simple load balancer that rotates through a list of servers.
    """

    def __init__(self, registration_service: RegistrationService, strategy: LoadBalancingStrategy = None):
        logger.info("Initializing LoadBalancer")
        self._registration_service = registration_service
        self._strategy = strategy or RoundRobinLoadBalancingStrategy(list(registration_service.get_addresses()))
        self._channels = {}
        registration_service.attach(self)

    def update(self, subject: RegistrationService):
        addresses = list(subject.get_addresses())
        logger.debug(f"LoadBalancer received update from {subject} with addresses {addresses}")
        self._strategy.update(addresses)
        self._channels = {address: grpc.aio.insecure_channel(str(address)) for address in addresses}

    async def send_meteo_data(self, meteo_data: RawMeteoData):
        logger.debug(f"Received meteo data {format_proto_msg(meteo_data)}")
        address = self._strategy.get_address()
        channel = self._channels[address]
        stub = ProcessingServiceStub(channel)
        logger.debug(f"Sending meteo data to {address}")
        await stub.ProcessMeteoData(meteo_data)

    async def send_pollution_data(self, pollution_data: RawPollutionData):
        logger.debug(f"Received pollution data {format_proto_msg(pollution_data)}")
        address = self._strategy.get_address()
        channel = self._channels[address]
        stub = ProcessingServiceStub(channel)
        logger.debug(f"Sending pollution data to {address}")
        await stub.ProcessPollutionData(pollution_data)

    def __repr__(self):
        return f"{self.__class__.__name__}(strategy={self._strategy})"


class LoadBalancingStrategy(ABC):
    """
    A load balancing strategy.
    """

    @abstractmethod
    def get_address(self) -> Address:
        """
        Returns the address to send the next request to.
        """
        pass

    @abstractmethod
    def update(self, addresses: Sequence[Address]):
        """
        Updates the list of addresses.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class RandomLoadBalancingStrategy(LoadBalancingStrategy):
    """
    A load balancing strategy that chooses a random address from the list of addresses.
    """

    def __init__(self, addresses: Sequence[Address]):
        self._addresses = addresses

    def get_address(self) -> Address:
        if not self._addresses or len(self._addresses) == 0:
            raise ValueError("No servers available")
        return random.choice(self._addresses)

    def update(self, addresses: Sequence[Address]):
        self._addresses = addresses


class RoundRobinLoadBalancingStrategy(LoadBalancingStrategy):
    """
    A load balancing strategy that rotates through a list of addresses.
    """

    def __init__(self, addresses: Sequence[Address]):
        self._addresses = addresses
        self._index = 0

    def get_address(self) -> Address:
        if not self._addresses or len(self._addresses) == 0:
            raise ValueError("No servers available")
        address = self._addresses[self._index]
        self._index = (self._index + 1) % len(self._addresses)
        return address

    def update(self, addresses: Sequence[Address]):
        self._addresses = addresses
