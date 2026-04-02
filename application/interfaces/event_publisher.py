from abc import ABC, abstractmethod
from domain.events import DomainEvent


class IEventPublisher(ABC):

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Persists the event in the outbox"""
        pass