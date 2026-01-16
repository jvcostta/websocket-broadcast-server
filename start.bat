@echo off
echo ================================================
echo   WebSocket Broadcast Server - Quick Start
echo ================================================
echo.

REM Verificar se backend está instalado
if not exist "backend\venv" (
    echo [1/4] Criando ambiente virtual Python...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    echo [2/4] Instalando dependências do backend...
    pip install -r requirements.txt
    cd ..
) else (
    echo [1/4] Ambiente virtual já existe - OK
    echo [2/4] Dependências do backend - OK
)

REM Verificar se frontend está instalado
if not exist "frontend\node_modules" (
    echo [3/4] Instalando dependências do frontend...
    cd frontend
    call npm install
    cd ..
) else (
    echo [3/4] Dependências do frontend - OK
)

echo [4/4] Iniciando servidores...
echo.
echo ================================================
echo   Abrindo 2 janelas de terminal:
echo   1. Backend (Python/FastAPI) - Porta 8000
echo   2. Frontend (Vite/TypeScript) - Porta 3000
echo ================================================
echo.

REM Iniciar backend em nova janela
start "WebSocket Backend" cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM Aguardar backend iniciar
timeout /t 3 /nobreak > nul

REM Iniciar frontend em nova janela
start "WebSocket Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo   Servidores iniciados!
echo ================================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000 (abre automaticamente)
echo   Docs:     http://localhost:8000/docs
echo.
echo   Pressione qualquer tecla para fechar este prompt
echo   (os servidores continuarão rodando nas outras janelas)
echo ================================================
pause > nul
