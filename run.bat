@echo off
cd /d "%~dp0"
py -3 convert.py %*
if errorlevel 1 pause
