# ================== БЭКЕНД (Django) ==================
FROM python:3.13-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка pip
RUN python3 -m ensurepip && \
    pip3 install --upgrade pip setuptools

# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Копируем код проекта
COPY . .

# Порт по умолчанию
EXPOSE 8000

# Запуск Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
