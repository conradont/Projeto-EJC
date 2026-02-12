# Conectar o Supabase ao Projeto EJC

O backend está preparado para usar **PostgreSQL** e **Storage** do Supabase: banco para dados e buckets **privados** para fotos dos candidatos e logo do evento. A API gera **URLs assinadas** (temporárias, 1 h) para exibir as imagens; assim só quem usa o sistema acessa as fotos.

---

## 1. Banco de dados (PostgreSQL)

### Obter a connection string

1. Acesse [supabase.com](https://supabase.com) e abra seu projeto.
2. **Project Settings** → **Database**.
3. Em **Connection string**, escolha **URI** e copie a URL.
4. Substitua `[YOUR-PASSWORD]` pela senha do banco.

### Configurar na API

No `api/.env`:

```env
DATABASE_URL=postgresql://postgres.[ref]:SUA_SENHA@db.SEU_PROJECT_REF.supabase.co:5432/postgres
```

Ao subir a API, as tabelas (incluindo `participants` e `event_settings`) são criadas automaticamente.

---

## 2. Storage (fotos e logo) – buckets privados

As imagens ficam em buckets **privados**; a API gera **URLs assinadas** (válidas por 1 hora) quando alguém acessa uma foto ou a logo. Assim apenas quem usa a aplicação consegue ver as imagens.

### No painel do Supabase

1. **Storage** → **New bucket**.
2. Crie dois buckets **privados** (deixe **Public bucket** desmarcado):
   - `photos` (fotos dos participantes)
   - `logo` (logo do evento)

### No `api/.env`

Em **Project Settings** → **API** copie:

- **Project URL** → `SUPABASE_URL`
- **service_role** (secret) → `SUPABASE_SERVICE_ROLE_KEY`

Exemplo:

```env
SUPABASE_URL=https://sngevkhfgfarzhbwbuew.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Comportamento

| Recurso      | Sem Storage (só .env de DB)     | Com Storage (buckets privados)        |
|-------------|-----------------------------------|----------------------------------------|
| Fotos       | Salvas em `api/data/photos`       | Enviadas ao bucket `photos`; API guarda o path e gera signed URL ao servir |
| Logo        | Salva em `api/data/logo`         | Enviada ao bucket `logo`; path no banco; API gera signed URL ao servir |
| Acesso      | Arquivos locais                  | Quem acessa `/api/photos/...` ou `/api/logo` recebe um redirect para uma URL temporária (1 h) |

O frontend guarda apenas o **path** (ex.: `abc123.jpg`) em `participant.photo_path`. Ao exibir, chama `/api/photos/abc123.jpg` e a API redireciona para uma signed URL do Supabase. A logo funciona igual via `/api/logo`.

---

## 3. Resumo

| Onde        | O que fazer |
|------------|-------------|
| **Banco**  | `DATABASE_URL` no `api/.env`. |
| **Storage** | Buckets **privados** `photos` e `logo`; `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` no `api/.env`. |
| **API**    | `pip install -r requirements.txt` e `python run.py` (ou `uvicorn main:app --reload`). |

Sem as variáveis de Storage, a API continua usando arquivos locais em `api/data/photos` e `api/data/logo`.
