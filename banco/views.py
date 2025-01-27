from rest_framework import viewsets, status
from .models import Carteira, User, Transferencia
from banco.permissions import CarteiraUsuarioPermission, UsuarioPermission, UsuarioTransferenciaPermission
from .serializers import CarteiraModelSerializer, UsuarioModelSerializer, TransferenciaSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date
from datetime import datetime
from django.db import transaction
from rest_framework.exceptions import NotFound
from django.http import Http404




class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar os usuários do sistema.
    Utiliza o modelo `User` e a permissão `UsuarioPermission`.
    """
    queryset = User.objects.all()
    serializer_class = UsuarioModelSerializer
    permission_classes = [UsuarioPermission]


class TransferenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar as transferências entre usuários.
    Permite consultar e filtrar transferências por usuário e intervalo de datas.
    """
    queryset = Transferencia.objects.all().order_by('-data_transferencia')
    serializer_class = TransferenciaSerializer
    permission_classes = [UsuarioTransferenciaPermission]

    def get_object(self):
        """
        Traduz a mensagem de erro corresponde à consulta fornecida.
        """
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Nenhuma transferência corresponde à consulta fornecida.")

    def get_queryset(self):
        """
        Filtra as transferências para o usuário autenticado e por intervalo de datas.
        """
        queryset = self.queryset.filter(
            Q(usuario_origem=self.request.user) | Q(usuario_destino=self.request.user)
        )

        # Filtra por data de início e fim
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if data_inicio:
            data_inicio = self._parse_date(data_inicio, "Data de início inválida. Formato esperado: YYYY-MM-DD.")
            if isinstance(data_inicio, Response):
                return data_inicio
            queryset = queryset.filter(data_transferencia__gte=data_inicio)

        if data_fim:
            data_fim = self._parse_date(data_fim, "Data de fim inválida. Formato esperado: YYYY-MM-DD.", end_of_day=True)
            if isinstance(data_fim, Response):
                return data_fim
            queryset = queryset.filter(data_transferencia__lte=data_fim)

        return queryset

    def _parse_date(self, date_string, error_message, end_of_day=False):
        """
        Converte uma string de data em um objeto datetime 'timezone-aware'.
        """
        try:
            date = parse_date(date_string)
            if not date:
                raise ValueError()
            time = datetime.max.time() if end_of_day else datetime.min.time()
            return make_aware(datetime.combine(date, time))
        except ValueError:
            return Response({'erro': error_message}, status=status.HTTP_400_BAD_REQUEST)


class CarteiraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar as carteiras dos usuários.
    Inclui ações como consultar saldo, depositar e transferir saldo.
    """
    queryset = Carteira.objects.all()
    serializer_class = CarteiraModelSerializer
    permission_classes = [CarteiraUsuarioPermission, IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='consultar-meu-saldo')
    def consultar_saldo(self, request):
        """
        Consulta o saldo da carteira do usuário autenticado.
        """
        carteira = self._get_carteira(request.user)
        if isinstance(carteira, Response):
            return carteira
        return Response({'saldo': str(carteira.saldo)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='depositar-saldo')
    def depositar_saldo(self, request):
        """
        Realiza o depósito de saldo na carteira do usuário autenticado.
        """
        valor = self._get_valor(request)
        if isinstance(valor, Response):
            return valor

        carteira = self._get_carteira(request.user)
        if isinstance(carteira, Response):
            return carteira

        # Transação atômica para garantir a consistência dos dados
        with transaction.atomic():
            carteira.saldo += valor
            carteira.save()

        return Response({'mensagem': 'Depósito realizado com sucesso.', 'saldo_atual': str(carteira.saldo)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='transferir-saldo')
    def transferir_saldo(self, request):
        """
        Realiza a transferência de saldo entre usuários ( Do usuário autenticado para outros ).
        """
        valor = self._get_valor(request)
        if isinstance(valor, Response):
            return valor

        usuario_destino_id = request.data.get('usuario_destino')
        if not usuario_destino_id:
            return Response({'erro': 'O campo "usuario_destino" é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se o usuário de destino existe
        try:
            usuario_destino = User.objects.get(id=usuario_destino_id)
        except User.DoesNotExist:
            return Response({'erro': 'Usuário de destino não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user == usuario_destino:
            return Response({'erro': 'A transferência deve ser para um usuário que não seja você mesmo.'}, status=status.HTTP_400_BAD_REQUEST)

        # Recupera as carteiras de origem e destino
        carteira_origem = self._get_carteira(request.user)
        if isinstance(carteira_origem, Response):
            return carteira_origem

        carteira_destino = self._get_carteira(usuario_destino)
        if isinstance(carteira_destino, Response):
            return carteira_destino

        if carteira_origem.saldo < valor:
            return Response({'erro': 'Saldo insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

        # Transação atômica para garantir a consistência dos dados
        with transaction.atomic():
            carteira_origem.saldo -= valor
            carteira_destino.saldo += valor
            carteira_origem.save()
            carteira_destino.save()

            transferencia = Transferencia.objects.create(
                usuario_origem=request.user,
                usuario_destino=usuario_destino,
                valor=valor,
            )

        return Response({
            'mensagem': f'Transferência de {valor:.2f} para {usuario_destino.username} realizada com sucesso.',
            'saldo': f'{carteira_origem.saldo:.2f}',
            'transferencia_id': transferencia.id,
        }, status=status.HTTP_200_OK)

    def _get_carteira(self, user):
        """
        Recupera a carteira do usuário. Retorna erro caso não encontre.
        """
        carteira = self.queryset.filter(usuario=user).first()
        if not carteira:
            return Response({'erro': 'Carteira não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        return carteira

    def _get_valor(self, request):
        """
        Valida e converte o valor para as operações de depósito e transferência.
        """
        valor = request.data.get('valor')
        if not valor:
            return Response({'erro': 'O campo "valor" é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            valor = Decimal(valor)
        except (ValueError, TypeError):
            return Response({'erro': 'O valor deve ser numérico.'}, status=status.HTTP_400_BAD_REQUEST)
        if valor <= 0:
            return Response({'erro': 'O valor deve ser maior que zero.'}, status=status.HTTP_400_BAD_REQUEST)
        return valor
