@echo off
echo ==========================================
echo    FIGHT CLUB - SISTEMA COMPLETO
echo ==========================================
echo.

echo Iniciando servidor web...
start cmd /k "python web_server.py"

timeout /t 2

echo Abrindo site no navegador...
start http://localhost:8080

echo.
echo ==========================================
echo SERVIDOR INICIADO!
echo - Site: http://localhost:8080
echo - Para jogar: python main.py
echo ==========================================
echo.
pause