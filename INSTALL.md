# Instalação - Sistema EJC

O sistema **só funciona em um modo:** um servidor local (API + frontend) na porta 8000, iniciado pelo launcher. Não há suporte a “rodar frontend em uma porta e API em outra”.

## Pré-requisitos

- **Windows**
- **Python 3.10 ou 3.12** – o launcher tenta instalar via winget se não estiver instalado
- **Node.js** (opcional) – só necessário se ainda não existir a pasta `dist` (primeira execução após clonar o projeto) ou para gerar o pacote de release

## Execução (único modo)

### Opção A: Duplo-clique (recomendado)

1. Se for a primeira vez e não houver pasta `dist`: instale Node.js e execute na raiz do projeto:
   ```powershell
   npm install
   npm run build
   ```
2. Duplo-clique em **run-ejc.bat**.

O launcher vai:
- Usar ou criar a pasta `dist` (e rodar `npm run build` se tiver Node e `dist` não existir)
- Verificar/instalar Python (winget)
- Criar ambiente virtual `.venv` e instalar dependências da API
- Subir o servidor em http://localhost:8000 e abrir o navegador

### Opção B: Linha de comando

```powershell
npm start
```

(Equivalente a executar `run-ejc.ps1`.)

### Encerrar

Feche a janela do terminal ou use Ctrl+C no terminal onde o servidor está rodando.

## Gerar pacote para distribuição

Para entregar o sistema a quem não tem Node (e opcionalmente sem Python, se o launcher instalar):

```powershell
npm run build:release
```

Será criada a pasta **EJC-Release** com:
- `dist/` (frontend buildado)
- `api/` (código da API)
- `run-ejc.bat` e `run-ejc.ps1`

Distribua essa pasta (ex.: em .zip). O usuário extrai e dá duplo-clique em **run-ejc.bat**.  
Ver [EXECUTAVEL.md](EXECUTAVEL.md) para gerar um .exe a partir do launcher.

## Configuração (opcional)

### Variáveis de ambiente (API)

Arquivo `api/.env` (opcional):

```env
DATABASE_URL=sqlite:///./ejc_registration.db
PORT=8000
DEBUG=0
```

O banco SQLite e os arquivos (fotos, PDFs) ficam em `api/` e `api/data/`.

### Modo desenvolvimento (API com reload)

Só se precisar recarregar a API automaticamente ao editar código:

```env
DEBUG=1
```

E rode a API manualmente a partir da pasta `api/` com `uvicorn main:app --reload`. O frontend continua sendo servido pela mesma API após `npm run build`.

## Estrutura de diretórios

```
Projeto-EJC/
├── api/                    # Backend FastAPI
│   ├── main.py             # Aplicação (API + servir dist)
│   ├── config.py           # Configurações
│   ├── database/
│   ├── models/
│   └── services/
├── src/                    # Frontend React (código-fonte)
├── dist/                   # Frontend buildado (gerado)
├── run-ejc.bat             # Launcher
├── run-ejc.ps1             # Launcher (PowerShell)
└── build-release.ps1       # Gera EJC-Release
```

## Resolução de problemas

- **“Pasta dist não encontrada”**  
  Rode `npm install` e `npm run build` na raiz, ou use o pacote EJC-Release.

- **“Python não encontrado”**  
  Instale Python 3.10+ manualmente (https://www.python.org/downloads/) ou permita que o launcher use winget para instalar Python 3.12.

- **Porta 8000 em uso**  
  Altere `PORT` em `api/.env` ou feche o programa que está usando a porta 8000.

- **Erro ao conectar ao banco**  
  Verifique se a pasta `api/` tem permissão de escrita (criação de `api/data/` e do arquivo SQLite).
