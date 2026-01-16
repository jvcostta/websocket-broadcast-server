#!/bin/bash

echo "================================================"
echo "  WebSocket Broadcast Server - Quick Start"
echo "================================================"
echo ""

# Verificar se backend está instalado
if [ ! -d "backend/venv" ]; then
    echo "[1/4] Criando ambiente virtual Python..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    echo "[2/4] Instalando dependências do backend..."
    pip install -r requirements.txt
    cd ..
else
    echo "[1/4] Ambiente virtual já existe - OK"
    echo "[2/4] Dependências do backend - OK"
fi

# Verificar se frontend está instalado
if [ ! -d "frontend/node_modules" ]; then
    echo "[3/4] Instalando dependências do frontend..."
    cd frontend
    npm install
    cd ..
else
    echo "[3/4] Dependências do frontend - OK"
fi

echo "[4/4] Iniciando servidores..."
echo ""
echo "================================================"
echo "  Abrindo 2 processos em background:"
echo "  1. Backend (Python/FastAPI) - Porta 8000"
echo "  2. Frontend (Vite/TypeScript) - Porta 3000"
echo "================================================"
echo ""

# Iniciar backend em background
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
sleep 3

# Iniciar frontend em background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================================"
echo "  Servidores iniciados!"
echo "================================================"
echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  Docs:     http://localhost:8000/docs"
echo ""
echo "  Backend PID:  $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "  Para parar os servidores:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "  Pressione Ctrl+C para encerrar"
echo "================================================"

# Aguardar interrupção
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait
