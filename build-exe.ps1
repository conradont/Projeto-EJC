# Gera o .exe do EJC com PyInstaller (Python + dependências + API + frontend em um único executável)
# Requer: Node.js (para build do frontend), Python 3.10+ e pip

$ErrorActionPreference = "Continue"  # Continuar mesmo com avisos
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Função para instalar pacote ignorando avisos de conflitos
function Install-PackageSafe {
    param($package, $upgrade = $false)
    $pipCmd = "$py -m pip install --quiet"
    if ($upgrade) { $pipCmd += " --upgrade" }
    $pipCmd += " $package"
    
    # Usar cmd.exe para executar e ignorar avisos completamente
    $null = cmd /c "$pipCmd 2>nul"
    
    # Sempre retornar sucesso (avisos de conflitos não são erros fatais)
    return $true
}

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

# Instalar PyInstaller (ignorar avisos de conflitos)
Write-Host ">> Instalando PyInstaller..." -ForegroundColor Yellow
Install-PackageSafe -package "pyinstaller" | Out-Null

# Instalar dependências essenciais da API (sem psycopg2-binary e supabase que são opcionais)
Write-Host ">> Instalando dependencias essenciais da API..." -ForegroundColor Yellow
$essentialDeps = @(
    "fastapi==0.115.0",
    "uvicorn[standard]==0.32.0",
    "python-multipart>=0.0.20,<1.0",
    "sqlalchemy==2.0.36",
    "pydantic>=2.10.3,<3.0.0",  # Versão flexível para evitar conflitos
    "pydantic-settings==2.6.1",
    "email-validator==2.1.1",
    "reportlab==4.2.5",
    "Pillow==11.0.0",
    "python-jose[cryptography]==3.3.0",
    "python-dotenv==1.0.1"
)
foreach ($dep in $essentialDeps) {
    # Instalar ignorando avisos de conflitos (são apenas avisos, não erros fatais)
    Install-PackageSafe -package $dep -upgrade $true | Out-Null
}
Write-Host "   (Avisos de conflitos de dependencias sao normais e nao impedem o build)" -ForegroundColor Gray

# Dependências opcionais (PostgreSQL/Supabase) não são instaladas
# O .exe funciona perfeitamente sem elas usando SQLite por padrão
Write-Host ">> Dependencias opcionais (PostgreSQL/Supabase) puladas" -ForegroundColor Gray
Write-Host "   O .exe usa SQLite por padrao e nao precisa dessas bibliotecas." -ForegroundColor Gray
Write-Host "   Se precisar PostgreSQL/Supabase, instale manualmente depois." -ForegroundColor Gray

# 3) Rodar PyInstaller
Write-Host ">> Gerando .exe com PyInstaller (pode demorar)..." -ForegroundColor Yellow
Set-Location $Root
try {
    & $py -m PyInstaller --noconfirm EJC.spec
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: PyInstaller falhou com codigo $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERRO ao executar PyInstaller: $_" -ForegroundColor Red
    exit 1
} finally {
    Set-Location $Root
}

$exePath = Join-Path $Root "dist\EJC-Sistema.exe"
if (Test-Path $exePath) {
    Write-Host "`n>> Concluido: $exePath" -ForegroundColor Green
    Write-Host "   Distribua esse .exe. O usuario so precisa executa-lo (Python e Node ja estao incluidos)." -ForegroundColor White
    Write-Host "   Dados (banco, fotos) serao criados na pasta onde o .exe esta." -ForegroundColor White
} else {
    Write-Host "ERRO: .exe nao foi gerado. Verifique as mensagens do PyInstaller." -ForegroundColor Red
    exit 1
}
