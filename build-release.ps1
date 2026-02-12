# Build do pacote de distribuição EJC
# Gera a pasta EJC-Release com frontend buildado, API e launcher (executável)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReleaseDir = Join-Path $Root "EJC-Release"

Write-Host "`n=== Build de Release - EJC Sistema ===" -ForegroundColor Cyan

# 1) Build do frontend (precisa de Node instalado)
Write-Host "`n>> Build do frontend (npm run build)..." -ForegroundColor Yellow
Set-Location $Root
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERRO: npm run build falhou. Instale Node.js e execute npm install." -ForegroundColor Red
    exit 1
}
Write-Host "   OK." -ForegroundColor Green

# 2) Limpar e criar pasta de release
if (Test-Path $ReleaseDir) { Remove-Item $ReleaseDir -Recurse -Force }
New-Item -ItemType Directory -Path $ReleaseDir | Out-Null

# 3) Copiar dist
Write-Host ">> Copiando frontend (dist)..." -ForegroundColor Yellow
Copy-Item -Path (Join-Path $Root "dist") -Destination (Join-Path $ReleaseDir "dist") -Recurse
Write-Host "   OK." -ForegroundColor Green

# 4) Copiar api (excluir cache e arquivos sensíveis)
Write-Host ">> Copiando API..." -ForegroundColor Yellow
$apiSrc = Join-Path $Root "api"
$apiDst = Join-Path $ReleaseDir "api"
Copy-Item -Path $apiSrc -Destination $apiDst -Recurse -Force
# Remover pastas/arquivos que não devem ir no pacote
@("__pycache__", "trash", ".venv") | ForEach-Object {
    $d = Join-Path $apiDst $_
    if (Test-Path $d) { Remove-Item $d -Recurse -Force }
}
Get-ChildItem $apiDst -Recurse -Include "*.db-wal", "*.db-shm" | Remove-Item -Force -ErrorAction SilentlyContinue
if (Test-Path (Join-Path $apiDst ".env")) { Remove-Item (Join-Path $apiDst ".env") -Force }
Write-Host "   OK." -ForegroundColor Green

# 5) Copiar launchers
Write-Host ">> Copiando launcher..." -ForegroundColor Yellow
Copy-Item (Join-Path $Root "run-ejc.ps1") -Destination (Join-Path $ReleaseDir "run-ejc.ps1") -Force
Copy-Item (Join-Path $Root "run-ejc.bat") -Destination (Join-Path $ReleaseDir "run-ejc.bat") -Force
Write-Host "   OK." -ForegroundColor Green

# 6) Criar README na release
$readme = @"
EJC Sistema - Pacote para execução local
(Único modo: um servidor em http://localhost:8000)

Como rodar:
  1. Duplo-clique em run-ejc.bat (ou run-ejc.ps1 no PowerShell)
  2. Na primeira execução o launcher pode instalar Python via winget (se nao tiver)
  3. O navegador abrira em http://localhost:8000

Requisitos: Windows. Python 3.10+ (instalado pelo launcher se faltar).
Node nao e necessario; o frontend ja esta buildado em dist/.

Dados: banco SQLite e arquivos ficam em api/ e api/data/.
"@
Set-Content -Path (Join-Path $ReleaseDir "LEIA-ME.txt") -Value $readme -Encoding UTF8

Write-Host "`n>> Concluido: $ReleaseDir" -ForegroundColor Green
Write-Host "   Para distribuir: compacte a pasta EJC-Release em .zip e envie." -ForegroundColor White
Write-Host "   O usuario so precisa extrair e dar duplo-clique em run-ejc.bat.`n" -ForegroundColor White
