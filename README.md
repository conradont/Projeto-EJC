# Sistema EJC

Sistema de gerenciamento de participantes do Encontro de Jovens com Cristo (EJC).  
**Funciona em modo único:** um servidor local (API + frontend) na porta 8000, iniciado pelo launcher.

## Como rodar (único modo suportado)

1. **Duplo-clique em `run-ejc.bat`** (ou no PowerShell: `.\run-ejc.ps1`, ou `npm start`).
2. Na primeira vez:
   - Se não existir a pasta `dist`, o launcher tenta fazer o build do frontend (é preciso ter Node.js).
   - Se não tiver Python, o launcher tenta instalar Python 3.12 via winget.
3. O navegador abre em **http://localhost:8000**.

**Requisitos:** Windows. Python 3.10+ (instalado automaticamente via winget se faltar). Node.js só é necessário na primeira execução se ainda não houver pasta `dist` (ou use o pacote EJC-Release).

## Gerar pacote para distribuir

**Opção 1 – Um único .exe (recomendado para usuário final)**  
Na raiz do projeto (com Node e Python):

```powershell
.\build-exe.ps1
```

Será gerado **dist\EJC-Sistema.exe**. Distribua só esse arquivo: o usuário não precisa instalar Python nem Node. Dados (banco, fotos) são criados na pasta onde o .exe está.

**Opção 2 – Pasta com launcher**  
```powershell
npm run build:release
```

Gera a pasta **EJC-Release** (frontend + API + run-ejc.bat). O usuário precisa ter (ou instalar) Python; o launcher pode instalar via winget.

Ver [EXECUTAVEL.md](EXECUTAVEL.md) para mais detalhes e para converter o launcher em .exe separado.

## Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind, Radix UI  
- **Backend:** FastAPI, SQLAlchemy, SQLite (ou PostgreSQL via env), ReportLab (PDFs)

## Estrutura

```
Projeto-EJC/
├── api/              # Backend FastAPI (uma única API serve tudo)
├── src/              # Frontend React (build vira dist/)
├── dist/             # Frontend buildado (gerado por npm run build)
├── run-ejc.bat       # Launcher (duplo-clique)
├── run-ejc.ps1       # Launcher (PowerShell)
└── build-release.ps1 # Gera EJC-Release para distribuição
```

## Configuração (opcional)

Arquivo `api/.env` (opcional):

```env
DATABASE_URL=sqlite:///./ejc_registration.db
PORT=8000
```

Documentação da API: **http://localhost:8000/docs** (quando o servidor estiver rodando).

## Instalação detalhada

Ver [INSTALL.md](INSTALL.md).
