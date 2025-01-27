from django.db import models
from django.contrib.auth.models import User

class Carteira(models.Model):
    """
    Representa a carteira de um usuário, contendo o saldo associado.
    """
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)  # Relaciona a carteira a um usuário.
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Saldo disponível na carteira.

    def __str__(self):
        return self.usuario.username  # Retorna o nome do usuário como representação.

class Transferencia(models.Model):
    """
    Representa uma transferência de saldo entre usuários.
    """
    usuario_origem = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transferencias_origem')  # Usuário que enviou o saldo.
    usuario_destino = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transferencias_destino')  # Usuário que recebeu o saldo.
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Valor da transferência.
    data_transferencia = models.DateTimeField(auto_now_add=True)  # Data e hora da transferência.

    def __str__(self):
        return f"Transferência de {self.usuario_origem.username} para {self.usuario_destino.username} - {self.valor}"  # Retorna detalhes da transferência.
