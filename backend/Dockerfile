FROM python:3.10-slim

WORKDIR /app

# Instala dependências
COPY backend/requirements.txt backend/requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

# Copia código da aplicação
COPY backend/ .

# Copia testes da raiz do projeto
COPY tests/ /tests/

# Configura PYTHONPATH para que os testes possam importar módulos do backend
ENV PYTHONPATH=/app:$PYTHONPATH

# Expõe porta do servidor
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["python", "main.py"]
