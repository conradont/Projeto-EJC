# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: gera .exe com Python + dependências + api + frontend (dist)
# Uso: pyinstaller EJC.spec
# Pré-requisito: npm run build (pasta dist) e pip install -r api/requirements.txt

import os
import sys

# Raiz do projeto (rodar pyinstaller na raiz: pyinstaller EJC.spec)
ROOT = os.getcwd()
DIST_FRONTEND = os.path.join(ROOT, 'dist')
API_FOLDER = os.path.join(ROOT, 'api')

# Incluir dist e api como dados (extraídos para _MEIPASS ao rodar)
# api: código da API; dist: frontend buildado
datas = [(DIST_FRONTEND, 'dist'), (API_FOLDER, 'api')]

# Módulos que o launcher e main importam (PyInstaller pode não detectar todos)
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'starlette.routing',
    'starlette.staticfiles',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'pydantic',
    'pydantic_settings',
    'multipart',
    'email_validator',
    'reportlab',
    'PIL',
    'PIL.Image',
    'jose',
    'dotenv',
    'psycopg2',
    'supabase',
]

a = Analysis(
    [os.path.join(ROOT, 'ejc_launcher.py')],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EJC-Sistema',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True = janela do console (ver logs); False = sem janela
)
