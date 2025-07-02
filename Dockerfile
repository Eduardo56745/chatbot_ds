# Usar imagen oficial con Python 3.10
FROM python:3.10-slim

# Variables de entorno para evitar buffers
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiar requirements (o instalamos directo)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y modelos
COPY . .

# Exponer puerto (el que uses en uvicorn, por defecto 8000)
EXPOSE 8000

# Comando para ejecutar uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


