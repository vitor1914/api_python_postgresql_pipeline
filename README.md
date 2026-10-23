# API → Python → PostgreSQL | Data Engineering Pipeline

## 🇧🇷 Português

Projeto de engenharia de dados que consome dados de uma API REST pública, transforma e valida os registros com Python e carrega os resultados em um banco PostgreSQL.

### Arquitetura

`JSONPlaceholder API → Python (requests + pandas) → PostgreSQL`

### Funcionalidades

- Extração de usuários e publicações via API REST.
- Timeout e tratamento de erros HTTP.
- Limpeza e validação básica dos dados.
- Carga idempotente com `INSERT ... ON CONFLICT DO UPDATE`.
- Tabelas relacionadas por chave estrangeira.
- Logs em arquivo e no console.
- Configuração por variáveis de ambiente.
- Consultas SQL para análise.
- PostgreSQL local via Docker Compose (opcional).

### Tecnologias

Python 3.10+, PostgreSQL, SQLAlchemy, psycopg2, requests, pandas, python-dotenv e Docker Compose (opcional).

### Estrutura

```text
api_python_postgresql_pipeline/
├── src/
│   ├── __init__.py
│   ├── api_client.py
│   ├── database.py
│   ├── transform.py
│   └── pipeline.py
├── sql/
│   └── analytics.sql
├── logs/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Pré-requisitos

- Python 3.10 ou superior.
- PostgreSQL instalado ou Docker.
- Acesso à internet para consumir a API.

### 1. Configurar o projeto

Crie e ative um ambiente virtual na pasta do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Iniciar PostgreSQL

**Opção A — Docker Compose**

Se tiver Docker e o plugin Compose instalados:

```bash
docker compose up -d
```

**Opção B — PostgreSQL já instalado**

Crie um banco chamado `data_pipeline` e ajuste as credenciais no arquivo `.env`.

### 3. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e revise os valores. Nunca publique o arquivo `.env`.

Linux:

```bash
cp .env.example .env
```

Configuração padrão para o Docker Compose deste projeto:

```env
API_BASE_URL=https://jsonplaceholder.typicode.com
DATABASE_URL=postgresql+psycopg2://pipeline_user:pipeline_password@localhost:5432/data_pipeline
API_TIMEOUT=30
LOG_LEVEL=INFO
```

### 4. Executar o pipeline

Na raiz do projeto, com o ambiente virtual ativado:

```bash
python -m src.pipeline
```

O pipeline cria as tabelas, extrai os dados, valida e transforma os registros e realiza a carga no PostgreSQL. Ao executar novamente, os registros existentes são atualizados pela chave primária, evitando duplicação.

### 5. Consultar os dados

Execute as instruções de `sql/analytics.sql` em pgAdmin, DBeaver ou `psql`.

Exemplos:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM posts;

SELECT u.name, COUNT(p.id) AS total_posts
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
GROUP BY u.id, u.name
ORDER BY total_posts DESC, u.name;
```

### Tabelas

- `users`: identificador da API, nome, nome de usuário, e-mail, cidade e empresa.
- `posts`: identificador da API, usuário relacionado, título e conteúdo.
- A coluna `posts.user_id` referencia `users.id`.

### Observações

- JSONPlaceholder é uma API de demonstração; os dados não representam necessariamente pessoas ou operações reais.
- O projeto usa os IDs fornecidos pela API como chaves primárias, tornando a carga repetível.
- O exemplo não inclui agendamento automático. Para evolução, pode-se adicionar Airflow, Prefect, testes automatizados, Docker para a aplicação e integração contínua.
- Não armazene credenciais reais no repositório.

## 🇺🇸 English

This data engineering project extracts users and posts from a public REST API, validates and transforms the records with Python, and loads them into PostgreSQL.

### Architecture

`JSONPlaceholder API → Python (requests + pandas) → PostgreSQL`

### Features

- REST API extraction for users and posts.
- HTTP timeout and error handling.
- Basic data cleaning and validation.
- Idempotent loading using `INSERT ... ON CONFLICT DO UPDATE`.
- Relational tables with a foreign key.
- Console and file logging.
- Environment-based configuration.
- SQL analytics queries.
- Optional local PostgreSQL setup with Docker Compose.

### Stack

Python 3.10+, PostgreSQL, SQLAlchemy, psycopg2, requests, pandas, python-dotenv, and optional Docker Compose.

### Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start PostgreSQL with Docker Compose, if available:

```bash
docker compose up -d
```

Copy `.env.example` to `.env` and review the settings:

```bash
cp .env.example .env
```

Run the pipeline from the project root:

```bash
python -m src.pipeline
```

The pipeline creates the database tables, extracts and transforms API data, validates records, and loads the results into PostgreSQL. Re-running it updates existing records instead of duplicating them.

Run the SQL statements in `sql/analytics.sql` using pgAdmin, DBeaver, or `psql`.

### Data model

- `users`: API ID, name, username, email, city, and company.
- `posts`: API ID, related user ID, title, and body.
- `posts.user_id` references `users.id`.

### Notes

JSONPlaceholder is a demo API. The dataset is illustrative and should not be treated as real business data. The pipeline is not scheduled automatically. Possible improvements include automated tests, orchestration with Airflow or Prefect, containerizing the Python application, and continuous integration. Keep real credentials out of version control.
