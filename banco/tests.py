import pytest
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, Carteira
from decimal import Decimal



@pytest.fixture
def user():
    """Cria um usuário para os testes."""
    return User.objects.create_user(username="admin",email='admin@gmail.com', password="123456")

@pytest.fixture
def user_destino():
    """Cria outro usuario para os testes."""
    return User.objects.create_user(username="admin_destino",email='admindestino@gmail.com', password="123456")


@pytest.fixture
def api_client():
    """Instancia o cliente da API."""
    return APIClient()

@pytest.fixture
def token(user,api_client):
    """Gerar token para ser reutilizado."""
    
    data = {'username': user.username, 'password': '123456'}
    response = api_client.post('/api/v1/token/', data , format='json')
    return response.data['access']

@pytest.mark.django_db
def test_criar_usuario_com_token(api_client,token):
    """Testa a criação de um usuário sem token de autenticação."""

    # Dados para criação do novo usuário
    data = {
        'username': 'newuser',
        'password': 'newpassword',
        'email': 'newuser@example.com'
    }

    # Realizar a requisição para criar um novo usuário com autenticação (com token)
    response = api_client.post('/api/v1/usuarios/', data, format='json',HTTP_AUTHORIZATION=f'Bearer {token}')

    # Verificar se a resposta foi bem-sucedida
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_proibir_criar_usuario_sem_token(api_client):
    """Testa a criação de um usuário sem token de autenticação."""

    # Dados para criação do novo usuário
    data = {
        'username': 'newuser',
        'password': 'newpassword',
        'email': 'newuser@example.com'
    }

    # Realizar a requisição para criar um novo usuário sem autenticação (sem token)
    response = api_client.post('/api/v1/usuarios/', data, format='json')

    # Verificar se a resposta foi proibida devido à falta de autenticação
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
# Verificar se a mensagem de erro está correta
    assert 'detail' in response.data
    assert response.data['detail'] == 'As credenciais de autenticação não foram fornecidas.'  # Mensagem de erro esperada


@pytest.mark.django_db
def test_login_token(api_client, user):
    """Testa o login com usuário e senha para obter o token."""
    url = '/api/v1/token/'  # O endpoint para obter o token JWT
    data = {
        'username': user.username,
        'password': '123456'
    }

    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data
    token = response.data['access']
    assert token is not None

@pytest.mark.django_db
def test_access_rota_protegida_com_token(api_client, token):
    """Testa o acesso a uma rota protegida com o token JWT."""
    url = '/api/v1/'  # Substitua pela URL de sua rota protegida
    print(token)
    # Usando o token para fazer a requisição autenticada
    response = api_client.get(url,HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK


def test_proibir_access_rota_protegida_sem_token(api_client):
    """Testa o acesso a uma rota protegida sem token JWT."""
    url = '/api/v1/'  # Substitua pela URL de sua rota protegida
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_depositar_saldo_com_token(api_client, user, token):
    """Testa a funcionalidade de depositar saldo na carteira de um usuário."""
    
    # Criar carteira para o usuário
    carteira = Carteira.objects.create(usuario=user, saldo=Decimal('50.00'))
    
    print(token)
    
    # Dados para o depósito
    deposito_data = {
        'valor': '30.00'  # Valor a ser depositado
    }

    # Realizar a requisição de depósito
    response = api_client.post('/api/v1/carteiras/depositar-saldo/', deposito_data, format='json',HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Verificar se a resposta foi bem-sucedida
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar se o saldo foi atualizado corretamente
    carteira.refresh_from_db()
    assert carteira.saldo == Decimal('80.00')  # Saldo inicial + depósito


@pytest.mark.django_db
def test_proibir_deposito_valor_invalido(api_client, user, token):
    """Testa a tentativa de depositar um valor inválido (negativo ou zero)."""
    
    # Criar carteira para o usuário
    carteira = Carteira.objects.create(usuario=user, saldo=Decimal('50.00'))
    
    
    # Dados para o depósito inválido (valor negativo)
    deposito_data = {
        'valor': '-20.00'  # Valor inválido
    }

    # Realizar a requisição de depósito
    response = api_client.post('/api/v1/carteiras/depositar-saldo/', deposito_data, format='json',HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Verificar se a resposta foi mal-sucedida devido ao valor inválido
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'erro' in response.data  # A resposta deve conter um erro indicando o valor inválido
    
    # Verificar que o saldo não foi alterado
    carteira.refresh_from_db()
    assert carteira.saldo == Decimal('50.00')  # Saldo permanece o mesmo


@pytest.mark.django_db
def test_proibir_deposito_saldo_sem_token(api_client, user):
    """Testa a tentativa de depósito sem autorização (usuário não autenticado)."""
    
    # Dados para o depósito
    deposito_data = {
        'valor': '30.00'  # Valor a ser depositado
    }

    # Realizar a requisição de depósito sem credenciais (usuário não autenticado)
    response = api_client.post('/api/v1/carteiras/depositar-saldo/', deposito_data, format='json')
    
    # Verificar se a resposta foi proibida devido à falta de autenticação
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
@pytest.mark.django_db
def test_transferir_saldo_com_token(api_client, user, token, user_destino):
    """Testa a funcionalidade de transferir saldo entre carteiras de usuários."""
    
    # Criar carteiras para o usuário de origem e o usuário de destino
    carteira_origem = Carteira.objects.create(usuario=user, saldo=Decimal('100.00'))
    carteira_destino = Carteira.objects.create(usuario=user_destino, saldo=Decimal('50.00'))
    
    # Verificar saldo inicial
    assert carteira_origem.saldo == Decimal('100.00')
    assert carteira_destino.saldo == Decimal('50.00')
    
    # Dados para a transferência de saldo da carteira do user para o user_destino
    transferencia_data = {
        'valor': '30.00',  # Valor a ser transferido
        'usuario_destino': user_destino.id  # ID do usuário de destino
    }

    # Realizar a requisição de transferência
    response = api_client.post('/api/v1/carteiras/transferir-saldo/', transferencia_data, format='json', HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Verificar se a resposta foi bem-sucedida
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar se os saldos foram atualizados corretamente
    carteira_origem.refresh_from_db()
    carteira_destino.refresh_from_db()
        
    # O saldo do usuário origem deve ser reduzido em 30.00 e o saldo do destino aumentado em 30.00
    assert carteira_origem.saldo == Decimal('70.00')  # Saldo inicial - transferência
    assert carteira_destino.saldo == Decimal('80.00')  # Saldo inicial + transferência
    

@pytest.mark.django_db
def test_proibir_transferir_saldo_sem_token(api_client, user, user_destino):
    """Testa a funcionalidade de transferir saldo entre carteiras de usuários."""
    
    # Criar carteiras para o usuário de origem e o usuário de destino
    carteira_origem = Carteira.objects.create(usuario=user, saldo=Decimal('100.00'))
    carteira_destino = Carteira.objects.create(usuario=user_destino, saldo=Decimal('50.00'))
    
    # Verificar saldo inicial
    assert carteira_origem.saldo == Decimal('100.00')
    assert carteira_destino.saldo == Decimal('50.00')
    
    # Dados para a transferência de saldo da carteira do user para o user_destino
    transferencia_data = {
        'valor': '30.00',  # Valor a ser transferido
        'usuario_destino': user_destino.id  # ID do usuário de destino
    }

    # Realizar a requisição de transferência
    response = api_client.post('/api/v1/carteiras/transferir-saldo/', transferencia_data, format='json')
    
    # Verificar se a resposta foi bem-sucedida
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    