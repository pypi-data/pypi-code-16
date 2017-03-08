from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from report_system.serializers import CreateTicketSerializer
from .models import Ticket, TicketType
from report_system.signals import signals
# Create your views here.


def perform_close(request, ticket):
    ticket.is_closed = True
    ticket.save()
    signals.ticket_was_closed.send(
        sender=Ticket,
        ticket=ticket,
        request=request,
    )


class CreateTicketView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateTicketSerializer

    def create(self, request, *args, **kwargs):
        target_model = kwargs['target_model']
        object_id = kwargs['id']
        data = request.data.copy()
        data['content_type'] = target_model
        data['object_pk'] = object_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
