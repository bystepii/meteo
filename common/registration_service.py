import logging
from typing import NamedTuple, Optional

from common.observer import Observable, Observer

logger = logging.getLogger(__name__)


class Address(NamedTuple):
    address: str
    port: int
    additional_info: Optional[str] = None

    def __repr__(self):
        return f"{self.address}:{self.port}" + (f" ({self.additional_info})" if self.additional_info else "")


class RegistrationService(Observable):
    """
    A simple registration service that keeps track of registered addresses (clients/servers).
    """

    def __init__(self, parent_service: str = None):
        logger.info("Initializing RegistrationService")
        self._parent_service = parent_service
        self._addresses: set[Address] = set()
        self._addresses_by_uid: dict[str, Address] = {}
        self._index = 0
        self._observers: set[Observer] = set()

    async def register(self, uid: str, address: Address):
        if address in self._addresses:
            logger.error(f"{self}: address {address} already registered")
            raise ValueError(f"Address {address} already registered")
        self._addresses.add(address)
        self._addresses_by_uid[uid] = address
        logger.info(f"{self} registered address {address}")
        self.notify()

    async def unregister(self, uid: str):
        try:
            addr = self._addresses_by_uid[uid]
            self._addresses.remove(addr)
            logger.info(f"{self}: unregistered address {addr} with uid {uid}")
            self.notify()
        except KeyError:
            pass

    def get_addresses(self) -> set[Address]:
        return self._addresses

    def attach(self, observer: Observer):
        self._observers.add(observer)
        logger.debug(f"{self}: attached observer {observer}")

    def detach(self, observer: Observer):
        self._observers.remove(observer)
        logger.debug(f"{self}: detached observer {observer}")

    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def __str__(self):
        return f"RegistrationService(parent_service={self._parent_service})"
