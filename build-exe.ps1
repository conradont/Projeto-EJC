# Gera o .exe do EJC com PyInstaller (Python + dependências + API + frontend em um único executável)
# Requer: Node.js (para build do frontend), Python 3.10+ e pip

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n=== Build do executável EJC-Sistema ===" -ForegroundColor Cyan

# 1) Frontend: garantir que dist existe
$distPath = Join-Path $Root "dist"
if (-not (Test-Path $distPath)) {
    Write-Host ">> Build do frontend (dist)..." -ForegroundColor Yellow
    Set-Location $Root
    npm run build
    if (-not (Test-Path $distPath)) {
        Write-Host "ERRO: npm run build nao gerou a pasta dist." -ForegroundColor Red
        exit 1
    }
    Set-Location $Root
} else {
    Write-Host ">> Pasta dist encontrada." -ForegroundColor Green
}

# 2) Python: ambiente e dependências da API
$py = $null
foreach ($cmd in @("py", "python3", "python")) {
    $p = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($p) {
        $ver = & $p --version 2>&1
        if ($ver -match "Python 3\.(\d+)") { $py = $p.Source; break }
    }
}
if (-not $py) {
    Write-Host "ERRO: Python 3 nao encontrado. Instale Python 3.10+." -ForegroundColor Red
    exit 1
}
Write-Host ">> Python: $py" -ForegroundColor Green

# Instalar PyInstaller e dependências da API
& $py -m pip install --quiet pyinstaller
& $py -m pip install --quiet -r (Join-Path $Root "api\requirements.txt")

# 3) Rodar PyInstaller
Write-Host ">> Gerando .exe com PyInstaller (pode demorar)..." -ForegroundColor Yellow
Set-Location $Root
& $py -m PyInstaller --noconfirm EJC.spec
Set-Location $Root

$exePath = Join-Path $Root "dist\EJC-Sistema.exe"
if (Test-Path $exePath) {
    Write-Host "`n>> Concluido: $exePath" -ForegroundColor Green
    Write-Host "   Distribua esse .exe. O usuario so precisa executa-lo (Python e Node ja estao incluidos)." -ForegroundColor White
    Write-Host "   Dados (banco, fotos) serao criados na pasta onde o .exe esta." -ForegroundColor White
} else {
    Write-Host "ERRO: .exe nao foi gerado. Verifique as mensagens do PyInstaller." -ForegroundColor Red
    exit 1
}
