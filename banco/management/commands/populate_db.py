from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from banco.models import Carteira, Transferencia  
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados fictícios para demonstração.'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Criando usuários fictícios
        for _ in range(10):  # Criar 10 usuários de exemplo
            usuario = User.objects.create_user(  # Usando create_user para garantir que a senha seja criptografada
                username=fake.user_name(),
                password='123456',
                email=fake.email()
            )

            # Criando carteiras associadas aos usuários
            carteira, created = Carteira.objects.get_or_create(
                usuario=usuario,  # Garantir que cada usuário tenha uma carteira associada
                defaults={'saldo': random.randint(100, 1000)}  # Gerando saldo aleatório entre 100 e 1000
            )

            # Criando transações fictícias
            for _ in range(5):  # Criar 5 transações por usuário
                # Escolhendo outro usuário para a transação (não pode ser o mesmo usuário)
                usuario_destino = User.objects.exclude(id=usuario.id).order_by('?').first()

                # Gerando valor aleatório para a transferência
                valor_transferencia = random.randint(10, 500)

                # Criando a transferência
                transferencia = Transferencia.objects.create(
                    usuario_origem=usuario,
                    usuario_destino=usuario_destino,
                    valor=valor_transferencia,
                )

                # Verificando se as carteiras de ambos os usuários existem
                try:
                    carteira_origem = Carteira.objects.get(usuario=usuario)
                    carteira_destino = Carteira.objects.get(usuario=usuario_destino)

                    # Subtraindo o valor da carteira do usuário de origem
                    if carteira_origem.saldo >= valor_transferencia:
                        carteira_origem.saldo -= valor_transferencia
                        carteira_origem.save()

                        # Adicionando o valor à carteira do usuário de destino
                        carteira_destino.saldo += valor_transferencia
                        carteira_destino.save()
                    else:
                        self.stdout.write(self.style.WARNING(f"Saldo insuficiente para a transferência de {usuario.username} para {usuario_destino.username}"))
                except Carteira.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Carteira não encontrada para um dos usuários na transferência de {usuario.username} para {usuario_destino.username}"))

        self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso!'))
