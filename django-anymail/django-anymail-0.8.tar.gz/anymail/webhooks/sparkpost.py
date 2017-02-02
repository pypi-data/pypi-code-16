import json
from datetime import datetime

from django.utils.timezone import utc

from .base import AnymailBaseWebhookView
from ..exceptions import AnymailConfigurationError
from ..signals import tracking, AnymailTrackingEvent, EventType, RejectReason


class SparkPostBaseWebhookView(AnymailBaseWebhookView):
    """Base view class for SparkPost webhooks"""

    def parse_events(self, request):
        raw_events = json.loads(request.body.decode('utf-8'))
        unwrapped_events = [self.unwrap_event(raw_event) for raw_event in raw_events]
        return [
            self.esp_to_anymail_event(event_class, event, raw_event)
            for (event_class, event, raw_event) in unwrapped_events
            if event is not None  # filter out empty "ping" events
        ]

    def unwrap_event(self, raw_event):
        """Unwraps SparkPost event structure, and returns event_class, event, raw_event

        raw_event is of form {'msys': {event_class: {...event...}}}

        Can return None, None, raw_event for SparkPost "ping" raw_event={'msys': {}}
        """
        event_classes = raw_event['msys'].keys()
        try:
            (event_class,) = event_classes
            event = raw_event['msys'][event_class]
        except ValueError:  # too many/not enough event_classes to unpack
            if len(event_classes) == 0:
                # Empty event (SparkPost sometimes sends as a "ping")
                event_class = event = None
            else:
                raise TypeError("Invalid SparkPost webhook event has multiple event classes: %r" % raw_event)
        return event_class, event, raw_event

    def esp_to_anymail_event(self, event_class, event, raw_event):
        raise NotImplementedError()


class SparkPostTrackingWebhookView(SparkPostBaseWebhookView):
    """Handler for SparkPost message, engagement, and generation event webhooks"""

    signal = tracking

    event_types = {
        # Map SparkPost event.type: Anymail normalized type
        'bounce': EventType.BOUNCED,
        'delivery': EventType.DELIVERED,
        'injection': EventType.QUEUED,
        'spam_complaint': EventType.COMPLAINED,
        'out_of_band': EventType.BOUNCED,
        'policy_rejection': EventType.REJECTED,
        'delay': EventType.DEFERRED,
        'click': EventType.CLICKED,
        'open': EventType.OPENED,
        'generation_failure': EventType.FAILED,
        'generation_rejection': EventType.REJECTED,
        'list_unsubscribe': EventType.UNSUBSCRIBED,
        'link_unsubscribe': EventType.UNSUBSCRIBED,
    }

    reject_reasons = {
        # Map SparkPost event.bounce_class: Anymail normalized reject reason.
        # Can also supply (RejectReason, EventType) for bounce_class that affects our event_type.
        # https://support.sparkpost.com/customer/portal/articles/1929896
        '1': RejectReason.OTHER,     # Undetermined (response text could not be identified)
        '10': RejectReason.INVALID,  # Invalid Recipient
        '20': RejectReason.BOUNCED,  # Soft Bounce
        '21': RejectReason.BOUNCED,  # DNS Failure
        '22': RejectReason.BOUNCED,  # Mailbox Full
        '23': RejectReason.BOUNCED,  # Too Large
        '24': RejectReason.TIMED_OUT,  # Timeout
        '25': RejectReason.BLOCKED,  # Admin Failure (configured policies)
        '30': RejectReason.BOUNCED,  # Generic Bounce: No RCPT
        '40': RejectReason.BOUNCED,  # Generic Bounce: unspecified reasons
        '50': RejectReason.BLOCKED,  # Mail Block (by the receiver)
        '51': RejectReason.SPAM,     # Spam Block (by the receiver)
        '52': RejectReason.SPAM,     # Spam Content (by the receiver)
        '53': RejectReason.OTHER,    # Prohibited Attachment (by the receiver)
        '54': RejectReason.BLOCKED,  # Relaying Denied (by the receiver)
        '60': (RejectReason.OTHER, EventType.AUTORESPONDED),  # Auto-Reply/vacation
        '70': RejectReason.BOUNCED,  # Transient Failure
        '80': (RejectReason.OTHER, EventType.SUBSCRIBED),  # Subscribe
        '90': (RejectReason.UNSUBSCRIBED, EventType.UNSUBSCRIBED),  # Unsubscribe
        '100': (RejectReason.OTHER, EventType.AUTORESPONDED),  # Challenge-Response
    }

    def esp_to_anymail_event(self, event_class, event, raw_event):
        if event_class == 'relay_event':
            # This is an inbound event
            raise AnymailConfigurationError(
                "You seem to have set SparkPost's *inbound* relay webhook URL "
                "to Anymail's SparkPost *tracking* webhook URL.")

        event_type = self.event_types.get(event['type'], EventType.UNKNOWN)
        try:
            timestamp = datetime.fromtimestamp(int(event['timestamp']), tz=utc)
        except (KeyError, TypeError, ValueError):
            timestamp = None

        try:
            tag = event['campaign_id']  # not 'rcpt_tags' -- those don't come from sending a message
            tags = [tag] if tag else None
        except KeyError:
            tags = None

        try:
            reject_reason = self.reject_reasons.get(event['bounce_class'], RejectReason.OTHER)
            try:  # unpack (RejectReason, EventType) for reasons that change our event type
                reject_reason, event_type = reject_reason
            except ValueError:
                pass
        except KeyError:
            reject_reason = None  # no bounce_class

        return AnymailTrackingEvent(
            event_type=event_type,
            timestamp=timestamp,
            message_id=event.get('transmission_id', None),  # not 'message_id' -- see SparkPost backend
            event_id=event.get('event_id', None),
            recipient=event.get('raw_rcpt_to', None),  # preserves email case (vs. 'rcpt_to')
            reject_reason=reject_reason,
            mta_response=event.get('raw_reason', None),
            # description=???,
            tags=tags,
            metadata=event.get('rcpt_meta', None) or None,  # message + recipient metadata
            click_url=event.get('target_link_url', None),
            user_agent=event.get('user_agent', None),
            esp_event=raw_event,
        )
