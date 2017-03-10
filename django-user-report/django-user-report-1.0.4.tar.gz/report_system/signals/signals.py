"""
Signals relating to tickets.
"""
from django.dispatch import Signal

ticket_was_closed = Signal(
    providing_args=["ticket", "request"]
)

target_was_inactivated = Signal(
    providing_args=["target"]
)
