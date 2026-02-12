# Launcher EJC - Verifica/instala Python compatível e inicia o app no navegador
# Requer: Node não é necessário em tempo de execução (frontend já buildado em dist/)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Cores e mensagens
function Write-Step { param($Msg) Write-Host "`n>> $Msg" -ForegroundColor Cyan }
function Write-Ok   { param($Msg) Write-Host "   $Msg" -ForegroundColor Green }
function Write-Warn { param($Msg) Write-Host "   $Msg" -ForegroundColor Yellow }
function Write-Err  { param($Msg) Write-Host "   $Msg" -ForegroundColor Red }

Write-Host "`n=== EJC Sistema - Iniciando ===" -ForegroundColor White

# 1) Verificar ou gerar pasta dist (frontend buildado)
$distPath = Join-Path $Root "dist"
if (-not (Test-Path $distPath)) {
    Write-Step "Pasta 'dist' nao encontrada. Tentando build do frontend..."
    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if ($npm) {
        Set-Location $Root
        if (-not (Test-Path (Join-Path $Root "node_modules"))) { npm install }
        npm run build
        Set-Location $Root
        if (-not (Test-Path $distPath)) {
            Write-Err "Build falhou ou dist nao foi criada."
            exit 1
        }
        Write-Ok "Frontend buildado."
    } else {
        Write-Err "Pasta 'dist' nao encontrada e npm nao esta disponivel."
        Write-Host "   Instale Node.js e execute: npm install && npm run build" -ForegroundColor Yellow
        Write-Host "   Ou use o pacote EJC-Release (gerado por build-release.ps1)." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Ok "Frontend (dist) encontrado."
}

# 2) Encontrar Python 3 (py, python3 ou python)
$pythonExe = $null
foreach ($cmd in @("py", "python3", "python")) {
    try {
        $p = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($p) {
            $ver = & $p --version 2>&1
            if ($ver -match "Python 3\.(\d+)") {
                $pythonExe = $p.Source
                Write-Ok "Python encontrado: $ver ($pythonExe)"
                break
            }
        }
    } catch {}
}

# 3) Se não tem Python, tentar instalar via winget
if (-not $pythonExe) {
    Write-Step "Python nao encontrado. Tentando instalar via winget (Python 3.12)..."
    try {
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
        # Atualizar PATH na sessão atual
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $pythonExe) { $pythonExe = (Get-Command py -ErrorAction SilentlyContinue).Source }
        if ($pythonExe) { Write-Ok "Python instalado. Reinicie o terminal se ainda falhar." }
    } catch {
        Write-Warn "winget falhou: $_"
    }
}

if (-not $pythonExe) {
    Write-Err "Python 3 nao encontrado. Instale manualmente: https://www.python.org/downloads/"
    Write-Host "   Versao recomendada: 3.10 ou 3.12" -ForegroundColor Yellow
    exit 1
}

# 4) Venv na pasta do projeto
$venvPath = Join-Path $Root ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Step "Criando ambiente virtual Python..."
    & $pythonExe -m venv $venvPath
    if (-not (Test-Path $venvPython)) { Write-Err "Falha ao criar .venv"; exit 1 }
    Write-Ok "Ambiente virtual criado."
}

# 5) Instalar dependências da API
$apiPath = Join-Path $Root "api"
$reqPath = Join-Path $apiPath "requirements.txt"
if (-not (Test-Path $reqPath)) { Write-Err "api/requirements.txt nao encontrado."; exit 1 }
Write-Step "Instalando/atualizando dependencias da API..."
& $venvPython -m pip install -r $reqPath -q
if ($LASTEXITCODE -ne 0) { Write-Err "Falha ao instalar dependencias."; exit 1 }
Write-Ok "Dependencias OK."

# 6) Abrir navegador após 2 segundos (em background)
$url = "http://localhost:8000"
Start-Process powershell -ArgumentList "-NoProfile -WindowStyle Hidden -Command", "Start-Sleep 2; Start-Process '$url'" -WindowStyle Hidden
Write-Ok "Navegador sera aberto em: $url"

# 7) Rodar API (servindo API + frontend estático); sem reload para estabilidade
Write-Step "Iniciando servidor (Ctrl+C para encerrar)..."
$env:DEBUG = "0"
Set-Location $apiPath
try {
    & (Join-Path $Root ".venv\Scripts\python.exe") -m uvicorn main:app --host 0.0.0.0 --port 8000
} finally {
    Set-Location $Root
}
