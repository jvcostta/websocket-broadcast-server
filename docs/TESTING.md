# Guia de Testes Automatizados

Este projeto possui uma suite completa de testes automatizados organizados por categoria.

## Estrutura de Testes

```
tests/
├── __init__.py
├── pyproject.toml              # Configuração do pytest
├── run_tests.py                # Script interativo de testes
├── backend/                    # Testes do backend
│   ├── __init__.py
│   ├── test_connection_manager.py   # Testes do gerenciador de conexões
│   ├── test_endpoints.py            # Testes dos endpoints da API
│   └── test_models.py               # Testes dos modelos Pydantic
└── integration/                # Testes de integração
    ├── __init__.py
    └── test_full_flow.py           # Testes end-to-end
```

## Tipos de Testes

### 1. Testes Unitários do Backend

#### `test_connection_manager.py`
Testa o gerenciamento do pool de conexões WebSocket:
- Conexão e desconexão de clientes
- Broadcast para todos os clientes
- Exclusão do remetente no broadcast
- Tratamento de erros de conexão
- Remoção automática de conexões com falha

#### `test_endpoints.py`
Testa os endpoints da API:
- Conexão WebSocket básica
- Envio e recebimento de mensagens
- Validação de JSON
- Tratamento de erros
- Broadcast entre múltiplos clientes

#### `test_models.py`
Testa os modelos Pydantic:
- Validação de dados de entrada
- Tratamento de campos obrigatórios
- Conversão de tipos
- Geração automática de timestamps

### 2. Testes de Integração

#### `test_full_flow.py`
Testa o fluxo completo do sistema:
- Broadcast entre múltiplos clientes reais
- Verificação de que remetente não recebe própria mensagem
- Envio rápido de múltiplas mensagens
- Desconexão e reconexão de clientes
- Tratamento de JSON inválido

## Instalação

### 1. Instalar dependências de teste

```bash
cd backend
pip install -r requirements-test.txt
```

### 2. Instalar dependências principais (se ainda não instalou)

```bash
pip install -r requirements.txt
```

## Executando os Testes

### Executar todos os testes

```bash
# Da raiz do projeto
pytest tests/

# Ou com mais detalhes
pytest tests/ -v
```

### Executar testes específicos

```bash
# Apenas testes do backend
pytest tests/backend/

# Apenas testes de integração
pytest tests/integration/

# Arquivo específico
pytest tests/backend/test_connection_manager.py

# Teste específico
pytest tests/backend/test_connection_manager.py::TestConnectionManager::test_connect
```

### Executar com cobertura de código

```bash
# Gerar relatório de cobertura
pytest tests/ --cov=backend --cov-report=html

# Ver relatório no navegador
# Abrir: htmlcov/index.html
```

### Executar apenas testes rápidos (excluir integração)

```bash
pytest tests/backend/ -v
```

### Executar com output detalhado

```bash
pytest tests/ -v -s  # -s mostra prints
```

## Notas Importantes

### Testes de Integração
Os testes de integração (`tests/integration/`) **requerem que o servidor esteja rodando**:

```bash
# Terminal 1: Iniciar o servidor
cd backend
python main.py

# Terminal 2: Executar testes de integração
pytest tests/integration/
```

Se o servidor não estiver rodando, estes testes serão **automaticamente pulados** (skip).

### Testes Assíncronos
Muitos testes usam `@pytest.mark.asyncio` para testar código assíncrono. O plugin `pytest-asyncio` é necessário.

## Boas Práticas

1. **Execute os testes antes de commit**
   ```bash
   pytest tests/backend/ -v
   ```

2. **Mantenha cobertura alta**
   - Objetivo: > 80% de cobertura
   - Use `--cov` para verificar

3. **Testes de integração separados**
   - Rodar apenas quando necessário
   - Requerem ambiente completo funcionando

4. **Nomenclatura clara**
   - `test_*` para funções de teste
   - `Test*` para classes de teste
   - Nomes descritivos do que está sendo testado

## Adicionando Novos Testes

### Exemplo de teste unitário

```python
def test_my_feature(manager):
    """Testa minha nova funcionalidade"""
    result = manager.do_something()
    assert result == expected_value
```

### Exemplo de teste assíncrono

```python
@pytest.mark.asyncio
async def test_async_feature(manager):
    """Testa funcionalidade assíncrona"""
    result = await manager.async_operation()
    assert result is not None
```

### Exemplo com mock

```python
from unittest.mock import MagicMock, AsyncMock

def test_with_mock():
    """Testa com mock"""
    mock_obj = MagicMock()
    mock_obj.method = AsyncMock(return_value="mocked")
    
    result = await mock_obj.method()
    assert result == "mocked"
    mock_obj.method.assert_called_once()
```

## CI/CD (Futuro)

Para integração contínua, adicionar ao pipeline:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt -r backend/requirements-test.txt
      - run: pytest tests/backend/ --cov=backend
```

## Troubleshooting

### `ModuleNotFoundError`
- Certifique-se de estar na raiz do projeto
- Verifique se os `__init__.py` existem

### Testes de integração falhando
- Verifique se o servidor está rodando
- Verifique a porta (padrão: 8000)
- Os testes devem dar skip automaticamente se não conseguir conectar

### ImportError do backend
- Os testes ajustam o `sys.path` automaticamente
- Se falhar, rode da raiz do projeto

## Comandos Úteis

```bash
# Executar e parar no primeiro erro
pytest tests/ -x

# Executar apenas testes que falharam na última vez
pytest tests/ --lf

# Executar em paralelo (requer pytest-xdist)
pytest tests/ -n auto

# Modo verbose com tempo de execução
pytest tests/ -v --durations=10
```

## Métricas de Qualidade

Execute periodicamente para manter a qualidade:

```bash
# Cobertura de código
pytest tests/backend/ --cov=backend --cov-report=term-missing

# Listar testes
pytest tests/ --collect-only

# Dry-run (não executa)
pytest tests/ --collect-only -q
```
