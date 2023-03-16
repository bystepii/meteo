import logging
from typing import Iterable

from common.observer import Observable, Observer

logger = logging.getLogger(__name__)


class RegistrationService(Observable):
    """
    A simple registration service that keeps track of registered addresses (clients/servers).
    """

    def __init__(self, addresses: Iterable[str] = None, parent_service: str = 'UnknownService'):
        logger.info("Initializing RegistrationService")
        self._addresses: set[str] = addresses or set()
        self._parent_service = parent_service
        self._index = 0
        self._observers: set[Observer] = set()

    def register(self, address: str) -> bool:
        if address in self._addresses:
            logger.warning(f"{self._parent_service} tried to register already registered address {address}")
            return False
        self._addresses.add(address)
        logger.info(f"{self._parent_service} registered address {address}")
        self.notify()
        return True

    def unregister(self, address: str):
        try:
            self._addresses.remove(address)
            logger.info(f"{self._parent_service} unregistered address {address}")
            self.notify()
        except KeyError:
            pass

    def get_addresses(self) -> set[str]:
        return self._addresses

    def attach(self, observer: Observer):
        self._observers.add(observer)
        logger.debug(f"{self._parent_service} attached observer {observer}")

    def detach(self, observer: Observer):
        self._observers.remove(observer)
        logger.debug(f"{self._parent_service} detached observer {observer}")

    def notify(self):
        for observer in self._observers:
            observer.update(self)
