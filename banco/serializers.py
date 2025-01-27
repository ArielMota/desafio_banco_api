from rest_framework import serializers
from .models import Carteira, User, Transferencia


class UsuarioModelSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo User. Inclui os campos básicos e uma configuração
    para garantir que a senha só pode ser escrita e não lida.
    """
    class Meta:
        model = User
        fields = ['id','username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}  # Senha só pode ser escrita.

    def create(self, validated_data):
        """
        Sobrescreve o método de criação para criar um usuário com senha criptografada
        e criar automaticamente uma carteira vinculada ao usuário.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')  # Email é opcional.
        )

        # Criação automática da carteira ao criar o usuário.
        Carteira.objects.create(usuario=user)
        return user


class CarteiraModelSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Carteira, incluindo o usuário associado.
    """
    usuario = UsuarioModelSerializer()  # Serializa o campo 'usuario' com informações completas.

    class Meta:
        model = Carteira
        fields = ['id', 'saldo', 'usuario']  # Inclui o ID, saldo e detalhes do usuário.


class TransferenciaSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Transferencia, adicionando o tipo da transferência
    (enviada ou recebida) com base no usuário autenticado.
    """
    tipo_transferencia = serializers.SerializerMethodField()  # Campo calculado.

    class Meta:
        model = Transferencia
        fields = ['id','usuario_origem', 'usuario_destino', 'valor', 'data_transferencia', 'tipo_transferencia']

    def get_tipo_transferencia(self, obj):
        """
        Retorna o tipo da transferência com base no usuário logado.
        """
        user = self.context['request'].user  # Obtém o usuário autenticado.
        if user == obj.usuario_origem:
            return 'Enviada'
        elif user == obj.usuario_destino:
            return 'Recebida'
        return 'Desconhecida'  # Para casos inesperados.
