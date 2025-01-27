# Projeto Django com API REST para Desafio de código Backend

Este é um projeto Django que expõe uma API REST para gerenciar usuários, carteiras e transações financeiras. A API é protegida por autenticação JWT (JSON Web Token) para garantir que apenas usuários autenticados possam acessar e modificar os dados.

## Requisitos

Antes de começar, certifique-se de que você tem as seguintes dependências instaladas:

- Python 3.11 ou superior
- Docker (para facilitar o uso de containers)
- Docker Compose (para orquestrar múltiplos containers)

## Instalação

### Passo 1: Clonar o repositório

Clone este repositório para sua máquina local:

```bash
git clone https://github.com/ArielMota/desafio_banco_api.git
cd desafio_banco_api
```

### Passo 2: Configuração do ambiente

Crie um arquivo `.env` na raiz do projeto com as variáveis de ambiente necessárias. Um exemplo de arquivo `.env`:

```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Passo 3: Construção e execução com Docker

Use o Docker Compose para construir e rodar o projeto:

```bash
docker-compose up --build
```

Isso irá:

1. Criar os containers do Django e PostgreSQL.
2. Rodar as migrações do banco de dados.

### Passo 4: Rodar as migrações do banco de dados

Após a execução do Docker Compose, execute o seguinte comando para aplicar as migrações:

```bash
docker-compose exec api python manage.py migrate
```

### Passo 5: Criar um superusuário (opcional)

Se você quiser criar um superusuário para acessar o Django Admin, execute o seguinte comando:

```bash
docker-compose exec api python manage.py createsuperuser
```

**Script `create_admin_user`:**
Este comando cria automaticamente um superusuário de admin com nome de usuário `admin`, e-mail `admin@gmail.com` e senha `123456`, caso ainda não exista um usuário admin no banco de dados. Você pode rodá-lo com:

```bash
docker-compose exec api python manage.py create_admin_user
```

### Passo 6: População do banco de dados com dados fictícios

O script `populate_db` cria 10 usuários fictícios, cada um com uma carteira associada e 5 transações aleatórias entre os usuários. Para rodá-lo, use o seguinte comando:

```bash
docker-compose exec api python manage.py populate_db
```

Este comando cria usuários e simula transações entre eles.

### Passo 7: Acessando a API

A API estará disponível na URL `http://localhost:8000`.

## Testes

Este projeto utiliza o **pytest** para testar a funcionalidade da API.

### Passo 1: Rodar os testes

Para rodar os testes, execute o seguinte comando dentro do container `api`:

```bash
docker-compose exec api pytest
```

Isso executará todos os testes definidos em `tests/` e mostrará os resultados no terminal.

### Passo 2: Testar a API com `pytest`

Se você precisar adicionar ou alterar os testes, você pode escrever novos testes no diretório `tests/` e rodar novamente o comando `pytest`.

## Endpoints da API

### 1. **Login (Obter Token)**

- **POST** `/api/v1/token/`
- **Parâmetros:**
  - `username`: Nome de usuário
  - `password`: Senha
- **Resposta:** Token JWT (Acessar com `Authorization: Bearer <token>`)

### 2. **Criar Usuário**

- **POST** `/api/v1/usuarios/`
- **Cabeçalho:**
  - `Authorization: Bearer <token>`
- **Parâmetros:**
  - `username`: Nome de usuário
  - `password`: Senha
  - `email`: E-mail
- **Resposta:** Status `201 Created` se o usuário for criado com sucesso.

### 3. **Depositar Saldo na Carteira**

- **POST** `/api/v1/carteiras/depositar-saldo/`
- **Cabeçalho:**
  - `Authorization: Bearer <token>`
- **Parâmetros:**
  - `valor`: Valor a ser depositado
- **Resposta:** Status `200 OK` se o depósito for bem-sucedido.

### 4. **Transferir Saldo entre Usuários**

- **POST** `/api/v1/carteiras/transferir-saldo/`
- **Cabeçalho:**
  - `Authorization: Bearer <token>`
- **Parâmetros:**
  - `valor`: Valor a ser transferido
  - `usuario_destino`: ID do usuário de destino
- **Resposta:** Status `200 OK` se a transferência for bem-sucedida.

### 5. **Listar Transferências do Usuário**

- **GET** `/api/v1/transferencias/`
- **Cabeçalho:**
  - `Authorization: Bearer <token>`
- **Parâmetros (opcionais):**
  - `data_inicio`: Data inicial para filtrar as transferências (formato `YYYY-MM-DD`).
  - `data_fim`: Data final para filtrar as transferências (formato `YYYY-MM-DD`).
- **Resposta:** Retorna a lista de transferências associadas ao usuário autenticado.
  - Se `data_inicio` e `data_fim` forem fornecidos, as transferências serão filtradas dentro do intervalo de datas especificado.

**Exemplo de requisição para listar transferências por intervalo de data:**

```http
GET /api/v1/transferencias/?data_inicio=2025-01-26&data_fim=2025-01-26
```

### 6. **Listar Carteira do Usuário**

- **GET** `/api/v1/carteiras/`
- **Cabeçalho:**
  - `Authorization: Bearer <token>`
- **Resposta:** Retorna os dados da carteira do usuário autenticado.

### 7. **Consultar Saldo da Carteira do Usuário**

- **GET** `/api/v1/carteiras/consultar-meu-saldo/`
- **Cabeçalho:**
  - `Authorization: Bearer <token>`
- **Resposta:** Retorna o saldo da carteira do usuário autenticado.

## Configuração do `REST_FRAMEWORK`

No projeto, utilizamos a configuração do `REST_FRAMEWORK` para garantir a segurança e a boa estruturação da API:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Utiliza JWT para autenticação
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # Requer autenticação para acessar os recursos
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',  # Paginação padrão com limite de resultados
    'PAGE_SIZE': 10  # Limite de resultados por página
}
```

### Explicação dos Recursos:

- **Autenticação JWT:**  
  Utilizamos o `JWTAuthentication` para autenticar os usuários via tokens JWT. Após o login, o usuário recebe um token que deve ser utilizado para acessar os endpoints da API, passando-o no cabeçalho da requisição com o formato `Authorization: Bearer <token>`.

- **Permissões:**  
  A permissão `IsAuthenticated` garante que somente usuários autenticados possam acessar os recursos da API. Isso significa que todos os endpoints protegidos exigem que o usuário tenha um token válido.

- **Paginação:**  
  A configuração `LimitOffsetPagination` é utilizada para paginar os resultados das consultas, permitindo limitar a quantidade de dados retornados por página. O tamanho da página é configurado como 10, ou seja, cada página retornará até 10 itens por vez. Se necessário, o usuário pode especificar o limite e o deslocamento usando os parâmetros `limit` e `offset` na URL da requisição.

## Estrutura de Diretórios

```
├── api/                # Contém a aplicação Django
├── docker-compose.yml  # Arquivo para orquestrar os containers Docker
├── Dockerfile          # Dockerfile para configurar o contêiner do Django
├── requirements.txt    # Arquivo com as dependências do Python
└── README.md           # Este arquivo
```

## Considerações Finais

Este projeto utiliza Docker para orquestrar os containers de desenvolvimento, facilitando a configuração e execução do projeto em diferentes ambientes. Certifique-se de que todos os containers estão funcionando corretamente e que o banco de dados foi configurado com sucesso.
