#!/usr/bin/env python3
"""
Script helper para executar testes
"""
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Executa comando e exibe resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    """Menu principal"""
    print("""
╔═══════════════════════════════════════════════╗
║   WebSocket Broadcast - Test Runner          ║
╚═══════════════════════════════════════════════╝

Escolha uma opção:
1. Executar todos os testes
2. Executar testes do backend
3. Executar testes de integração  
4. Executar com cobertura
5. Executar testes específicos
6. Listar todos os testes
0. Sair
""")
    
    choice = input("Opção: ").strip()
    
    commands = {
        '1': ("pytest tests/ -v", "Executando todos os testes"),
        '2': ("pytest tests/backend/ -v", "Executando testes do backend"),
        '3': ("pytest tests/integration/ -v", "Executando testes de integração"),
        '4': ("pytest tests/backend/ --cov=backend --cov-report=html --cov-report=term", "Executando com cobertura"),
        '5': (None, "Executando teste específico"),
        '6': ("pytest tests/ --collect-only", "Listando todos os testes"),
        '0': (None, "Saindo...")
    }
    
    if choice == '0':
        print("👋 Até logo!")
        return
    
    if choice == '5':
        test_path = input("Digite o caminho do teste: ").strip()
        run_command(f"pytest {test_path} -v", f"Executando {test_path}")
        return
    
    if choice in commands:
        cmd, desc = commands[choice]
        if cmd:
            success = run_command(cmd, desc)
            if success:
                print("\n✅ Testes executados com sucesso!")
            else:
                print("\n❌ Alguns testes falharam")
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    # Verificar se está na raiz do projeto
    if not Path("tests").exists():
        print("❌ Execute este script da raiz do projeto")
        sys.exit(1)
    
    # Verificar se pytest está instalado
    try:
        subprocess.run(["pytest", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest não está instalado")
        print("📦 Instale com: pip install -r backend/requirements-test.txt")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário")
        sys.exit(0)
