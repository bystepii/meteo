import random
from itertools import cycle

from typing import Set, Iterable, List

from common.abstract_listener import AbstractListener


class RegistrationService:
    """
    A simple registration service that keeps track of registered addresses (clients/servers).
    """

    def __init__(self, listener: AbstractListener = None, addresses: Iterable[str] = None):
        self._listener = listener
        self._addresses: List[str] = addresses or list()
        self._index = 0

    def register(self, address: str) -> bool:
        if address in self._addresses:
            return False
        self._addresses.append(address)
        if self._listener:
            self._listener.register(address)
        return True

    def unregister(self, address: str):
        try:
            self._addresses.remove(address)
            if self._listener:
                self._listener.unregister(address)
        except KeyError:
            pass

    def get_addresses(self) -> List[str]:
        return self._addresses

    def get_random_address(self) -> str:
        return random.choice(list(self._addresses))

    def get_next_address(self) -> str:
        address = self._addresses[self._index]
        self._index = (self._index + 1) % len(self._addresses)
        return address
