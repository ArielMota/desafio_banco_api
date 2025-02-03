from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from banco.models import Carteira  

class Command(BaseCommand):
    help = 'Cria automaticamente um usuário admin após as migrações'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = '123456'  # Defina uma senha segura
        email = 'admin@gmail.com'  # Email do usuário admin

        # Verifique se o usuário admin já existe
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'O usuário {username} já existe.'))
        except ObjectDoesNotExist:
            # Crie o usuário admin se não existir
            usuario = User.objects.create_superuser(username=username, email=email, password=password)
            # Criando carteiras associadas aos usuários
            carteira, created = Carteira.objects.get_or_create(
                usuario=usuario,  # Garantir que usuário tenha uma carteira associada
                defaults={'saldo': 10000}  # Gerando saldo aleatório entre 100 e 1000
            )
            self.stdout.write(self.style.SUCCESS(f'Usuário admin "{username}" criado com sucesso.'))