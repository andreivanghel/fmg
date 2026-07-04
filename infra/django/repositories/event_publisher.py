from application.interfaces.event_publisher import IEventPublisher
from domain.events import DomainEvent
from infra.django.models import OutboxEventORM


class DjangoOutboxEventPublisher(IEventPublisher):

    def publish(self, event: DomainEvent) -> None:
        OutboxEventORM.objects.create(
            event_type=event.event_type,
            payload=event.to_payload(),
            created_at=event.created_at
        )
