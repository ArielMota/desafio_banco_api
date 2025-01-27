from dj_rql.drf import RQLFilterBackend
from rest_framework import viewsets,permissions
from evento.filters import EventoFilterClass, ParticipanteFilterClass
from evento.models import Evento, Participante
from evento.permissions import EventoOrganizadorPermission
from evento.serializers import EventoModelSerializer, ParticipanteModelSerializer

class EventoModelViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = EventoFilterClass
    permission_classes = [permissions.DjangoModelPermissions, EventoOrganizadorPermission,]

class ParticipanteModelViewSet(viewsets.ModelViewSet):
    queryset = Participante.objects.all()
    serializer_class = ParticipanteModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = ParticipanteFilterClass