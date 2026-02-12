# Executável - EJC Sistema

Este documento descreve como rodar o app como “executável” (launcher que sobe o servidor e abre o navegador) e como opcionalmente converter o launcher em um `.exe`.

O projeto funciona apenas neste modo: launcher sobe um único servidor (API + frontend) e abre o navegador.

## O que foi implementado

- **run-ejc.bat** / **run-ejc.ps1**: launcher que:
  - Verifica ou gera a pasta `dist` (frontend buildado; se faltar, tenta `npm run build` quando Node está instalado)
  - Procura Python 3 (comando `py`, `python3` ou `python`)
  - Se não encontrar, tenta instalar **Python 3.12** via `winget`
  - Cria um ambiente virtual `.venv` na pasta do projeto e instala as dependências da API
  - Inicia o servidor (FastAPI servindo API + frontend estático na porta 8000)
  - Abre o navegador em http://localhost:8000

- **build-release.ps1**: gera o pacote de distribuição:
  - Roda `npm run build` (é preciso ter Node na máquina de build)
  - Cria a pasta **EJC-Release** com `dist/`, `api/`, `run-ejc.bat`, `run-ejc.ps1` e um LEIA-ME.txt

O usuário final **não precisa de Node**: o frontend já vai buildado em `dist/`. Só precisa de **Python**, que o launcher tenta instalar via winget se não existir.

## Uso rápido

### Desenvolvedor (gerar o pacote)

```powershell
# Na raiz do projeto (precisa de Node e Python)
.\build-release.ps1
```

Depois distribua a pasta **EJC-Release** (por exemplo, em .zip).

### Usuário final (rodar o app)

1. Extrair o conteúdo do .zip (ex.: na pasta `EJC-Release`).
2. Duplo-clique em **run-ejc.bat**.
3. Na primeira execução pode ser pedida a instalação do Python (via winget).
4. O navegador abre em http://localhost:8000.

## Converter o launcher em .exe (opcional)

Se quiser um único arquivo **run-ejc.exe** em vez de abrir o `.bat`:

1. **Usando PS2EXE** (PowerShell para .exe):
   - Instale o módulo: `Install-Module ps2exe -Scope CurrentUser`
   - Gere o .exe:
     ```powershell
     ps2exe -inputFile ".\run-ejc.ps1" -outputFile ".\EJC-Release\run-ejc.exe" -noConsole
     ```
   - O `-noConsole` esconde a janela do PowerShell; use sem ele se quiser ver as mensagens do launcher.

2. **Usando Bat to Exe Converter** (ou similar):
   - Crie um .bat que apenas chama o PowerShell:
     ```bat
     @echo off
     cd /d "%~dp0"
     powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-ejc.ps1"
     ```
   - Use o conversor para gerar um .exe a partir desse .bat. O .exe e o `run-ejc.ps1` devem ficar na mesma pasta (ex.: dentro de EJC-Release).

Coloque o **run-ejc.exe** dentro da pasta **EJC-Release** junto com `dist/`, `api/`, etc., e distribua. O usuário pode duplo-clicar no .exe em vez do .bat.

## .exe com tudo incluído (Python + dependências + projeto)

Para um **único executável** em que o usuário não precise instalar Python nem Node:

1. **Na sua máquina** (com Node e Python instalados), na raiz do projeto:
   ```powershell
   .\build-exe.ps1
   ```
   O script faz o build do frontend (se faltar `dist`), instala PyInstaller e as dependências da API e gera o .exe.

2. O executável é gerado em: **`dist\EJC-Sistema.exe`**.

3. **Distribua apenas esse .exe.** O usuário:
   - Cola o .exe em qualquer pasta (ex.: `C:\EJC\`)
   - Dá duplo-clique
   - O navegador abre em http://localhost:8000  
   - Banco de dados e arquivos (fotos, PDFs) são criados na **mesma pasta** do .exe (ou na subpasta `data`).

**O que vai dentro do .exe:** interpretador Python, FastAPI, uvicorn, SQLAlchemy, ReportLab, demais dependências da API, código da API e frontend (buildado). **Node não é incluído** (e não é necessário): o frontend já está compilado dentro do .exe.

**Requisitos para gerar o .exe:** Node.js (para `npm run build`), Python 3.10+ e pip. O usuário final não precisa de nada além do Windows.

### Opcional: esconder a janela do console

No arquivo **EJC.spec**, altere `console=True` para `console=False` na seção `EXE(...)`. Assim o .exe abre só o navegador, sem janela preta. Para ver logs de erro, use `console=True`.

## Versões compatíveis

- **Python:** 3.10 ou 3.12 (o launcher tenta instalar 3.12 via winget).
- **Node:** só é necessário na máquina onde você roda `build-release.ps1`; o usuário final não precisa de Node.

## Resumo de arquivos

| Arquivo            | Função |
|--------------------|--------|
| run-ejc.ps1        | Launcher principal (PowerShell). |
| run-ejc.bat        | Atalho para executar run-ejc.ps1 (duplo-clique). |
| build-release.ps1  | Gera a pasta EJC-Release (dist + api + launchers). |
| build-exe.ps1      | Gera o .exe único com PyInstaller (Python + deps + projeto). |
| ejc_launcher.py    | Ponto de entrada usado pelo PyInstaller. |
| EJC.spec           | Configuração do PyInstaller. |
| dist/EJC-Sistema.exe | Executável gerado por build-exe.ps1 (tudo incluído). |
| EJC-Release/       | Pasta para distribuir (run-ejc.bat + dist + api). |
