import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from typing_extensions import override


class EventType(StrEnum):
    CHECKS_REQUESTED = "checks_requested"


@dataclass(frozen=True, kw_only=True)
class DomainEvent(ABC):
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC), init=False)

    @property
    @abstractmethod
    def event_type(self) -> EventType:
        pass

    def to_payload(self) -> dict:
        """
        Transforms the subclass in a dictionary, excluding abstract field metadata.
        """
        data = dataclasses.asdict(self)

        # Removing abstract field metadata
        data.pop("created_at", None)
        return data

    def __post_init__(self):
        # Abstract class should not be instantiable
        if type(self) is DomainEvent:
            raise TypeError("Cannot instantiate abstract class DomainEvent.")

        # Non-empty payload validation
        if not self.to_payload():
            raise ValueError(f"Empty event: {self.__class__.__name__}.")


@dataclass(frozen=True)
class ChecksRequested(DomainEvent):
    run_id: int

    @override
    @property
    def event_type(self) -> EventType:
        return EventType.CHECKS_REQUESTED
