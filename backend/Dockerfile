FROM python:3.10-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Expõe porta do servidor
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["python", "main.py"]
