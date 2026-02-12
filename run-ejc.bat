@echo off
title EJC Sistema
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-ejc.ps1"
pause
