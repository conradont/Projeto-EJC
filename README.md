# Sistema EJC - Refatoração Moderna

Sistema de gerenciamento de participantes do Encontro de Jovens com Cristo (EJC), refatorado com tecnologias modernas.

## 🚀 Stack Tecnológica

### Frontend
- **React 19.1.1** - Biblioteca UI
- **TypeScript 5.8.3** - Tipagem estática
- **Vite 7.1.7** - Build tool
- **React Router DOM 7.9.1** - Roteamento
- **TanStack Query 5.90.2** - Gerenciamento de estado servidor
- **Axios 1.12.2** - Cliente HTTP
- **Tailwind CSS 4.1.13** - Estilização
- **React Hook Form 7.63.0** - Formulários
- **Zod 4.1.11** - Validação de schemas
- **Radix UI** - Componentes acessíveis
- **Sonner** - Notificações toast

### Backend
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM
- **Pydantic** - Validação de dados
- **ReportLab** - Geração de PDFs
- **SQLite** - Banco de dados

## 📁 Estrutura do Projeto

```
Projeto-EJC/
├── api/                    # Backend FastAPI
│   ├── main.py            # Aplicação principal
│   ├── config.py          # Configurações
│   ├── database/          # Camada de dados
│   │   ├── database.py   # Configuração DB
│   │   └── crud.py        # Operações CRUD
│   ├── models/            # Modelos SQLAlchemy/Pydantic
│   │   └── participant.py
│   └── services/         # Serviços de negócio
│       └── pdf_service.py # Geração de PDFs
├── src/                   # Frontend React
│   ├── components/        # Componentes React
│   ├── pages/            # Páginas
│   ├── lib/              # Utilitários e API
│   ├── schemas/          # Schemas Zod
│   └── types/            # Tipos TypeScript
├── package.json          # Dependências frontend
└── api/requirements.txt  # Dependências backend
```

## 🛠️ Instalação e Execução

### Pré-requisitos
- Node.js 18+ e npm/yarn
- Python 3.10+

### Backend (API)

```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Frontend

```bash
npm install
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

## 📝 Funcionalidades

- ✅ Cadastro de participantes
- ✅ Listagem com paginação e busca
- ✅ Edição de participantes
- ✅ Exclusão de participantes
- ✅ Geração de PDFs individuais
- ✅ Geração de PDF completo
- ✅ Validação de formulários
- ✅ Interface moderna e responsiva

## 🔧 Configuração

### Variáveis de Ambiente (API)

Crie um arquivo `.env` na pasta `api/`:

```env
DATABASE_URL=sqlite:///./ejc_registration.db
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 📚 Documentação da API

Acesse `http://localhost:8000/docs` para ver a documentação interativa da API (Swagger UI).

## 🎨 Desenvolvimento

### Estrutura de Componentes

- `Layout` - Layout principal com navegação
- `ParticipantForm` - Formulário de cadastro
- `ParticipantsList` - Lista de participantes
- `ReportsPanel` - Painel de geração de PDFs

### Hooks e Utilitários

- `useQuery` / `useMutation` - TanStack Query para dados
- `useForm` - React Hook Form para formulários
- `zodResolver` - Validação com Zod

## 📄 Licença

Este projeto é de uso interno para o EJC.
