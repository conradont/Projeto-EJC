# Deploy na Vercel (frontend + API)

O projeto está configurado para um único deploy na Vercel: o **FastAPI** serve a API em `/api/*` e o **frontend** (React) em `/` após o build.

## O que foi configurado

- **`app.py`** (raiz): entrypoint que a Vercel reconhece; importa o app de `api.main`.
- **`requirements.txt`** (raiz): dependências Python para o build.
- **`vercel.json`**: `buildCommand: npm run build` e `installCommand` para Node + Pip.
- **`api/main.py`**: em ambiente Vercel (`IS_VERCEL`), monta a pasta `dist` em `/` para servir o frontend.

## Passos para fazer o deploy

1. **Conecte o repositório** na [Vercel](https://vercel.com) (Import Project → Git).

2. **Variáveis de ambiente** (Settings → Environment Variables). Defina pelo menos:
   - `DATABASE_URL` – connection string do Supabase (PostgreSQL)
   - `SUPABASE_URL` – URL do projeto Supabase
   - `SUPABASE_SERVICE_ROLE_KEY` – chave **service_role** (secret)

   Opcional: `CORS_ORIGINS` se precisar de outros domínios.

3. **Build**: a Vercel vai rodar `npm install && pip install -r requirements.txt` e depois `npm run build`. O app Python usa o `dist` gerado.

4. **Não commite** o arquivo `.env`; use só as variáveis no painel da Vercel.

## Rodar localmente (igual ao dia a dia)

- **Frontend:** `npm run dev` (usa proxy para a API em `localhost:8000`).
- **API:** `cd api && python run.py` (ou `uvicorn main:app --reload` dentro de `api/`).

O `.env` fica em `api/.env`; não é necessário na raiz para desenvolvimento.

## Simular ambiente Vercel na máquina (opcional)

```bash
npm run build
pip install -r requirements.txt
set VERCEL=1
uvicorn app:app --host 0.0.0.0 --port 8000
```

Assim o app serve o `dist` em `/` e a API em `/api`. No Windows use `set VERCEL=1`; no Linux/macOS use `VERCEL=1 uvicorn ...`.
