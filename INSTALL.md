# Guia de Instalação - Sistema EJC

## Pré-requisitos

- **Node.js** 18+ e npm/yarn
- **Python** 3.10+
- **Git** (opcional)

## Instalação

### 1. Backend (API FastAPI)

```bash
# Navegar para a pasta da API
cd api

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar a API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Frontend (React + TypeScript)

```bash
# Na raiz do projeto
npm install

# Executar em modo desenvolvimento
npm run dev
```

O frontend estará disponível em: http://localhost:3000

## Estrutura de Diretórios

```
Projeto-EJC/
├── api/                    # Backend FastAPI
│   ├── main.py            # Aplicação principal
│   ├── config.py          # Configurações
│   ├── database/          # Camada de dados
│   ├── models/            # Modelos SQLAlchemy/Pydantic
│   └── services/          # Serviços de negócio
├── src/                   # Frontend React
│   ├── components/        # Componentes React
│   ├── pages/            # Páginas
│   ├── lib/              # Utilitários e API
│   ├── schemas/          # Schemas Zod
│   └── types/            # Tipos TypeScript
└── package.json          # Dependências frontend
```

## Configuração

### Variáveis de Ambiente (API)

Crie um arquivo `.env` na pasta `api/` (opcional):

```env
DATABASE_URL=sqlite:///./ejc_registration.db
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Banco de Dados

O banco de dados SQLite será criado automaticamente na primeira execução da API.

## Execução em Produção

### Backend

```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
npm run build
npm run preview
```

## Troubleshooting

### Erro ao instalar dependências Python

Certifique-se de estar usando Python 3.10+:
```bash
python --version
```

### Erro de CORS

Verifique se as URLs do frontend estão configuradas em `api/config.py` na lista `CORS_ORIGINS`.

### Erro ao conectar ao banco de dados

Certifique-se de que o diretório `api/data/` existe e tem permissões de escrita.

## Desenvolvimento

### Estrutura de Componentes React

- `Layout` - Layout principal com navegação
- `ParticipantForm` - Formulário de cadastro
- `ParticipantsList` - Lista de participantes
- `ReportsPanel` - Painel de geração de PDFs

### Endpoints da API

- `GET /api/participants` - Lista participantes
- `GET /api/participants/{id}` - Obtém participante
- `POST /api/participants` - Cria participante
- `PUT /api/participants/{id}` - Atualiza participante
- `DELETE /api/participants/{id}` - Exclui participante
- `GET /api/pdf/participant/{id}` - Gera PDF individual
- `GET /api/pdf/complete` - Gera PDF completo

## Próximos Passos

1. Configurar upload de fotos para o servidor
2. Implementar autenticação/autorização
3. Adicionar mais filtros na listagem
4. Implementar edição de participantes
5. Adicionar testes automatizados
