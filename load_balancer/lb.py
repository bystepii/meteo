import random

from common.observer import Observer
from common.registration_service import RegistrationService


class LoadBalancer(Observer):
    """
    A simple load balancer that rotates through a list of servers.
    """

    def __init__(self, registration_service: RegistrationService):
        self._registration_service = registration_service
        self._addresses = registration_service.get_addresses()
        self._index = 0

        registration_service.attach(self)

    def get_random_address(self) -> str:
        return random.choice(list(self._addresses))

    def get_next_address(self) -> str:
        address = self._addresses[self._index]
        self._index = (self._index + 1) % len(self._addresses)
        return address

    def update(self, subject: RegistrationService):
        self._addresses = subject.get_addresses()
