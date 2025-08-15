# //////////////////PRODUCION CONTAINER////////////////////////
# # Создать образ на основе базового слоя,
# # который содержит файлы ОС и интерпретатор Python 3.12.
# FROM python:3.13-slim

# # Установка базовых зависимостей
# RUN apt-get update && \
#     apt-get install -y build-essential libssl-dev zlib1g-dev \
#     libbz2-dev libreadline-dev libsqlite3-dev wget \
#     curl llvm libncurses5-dev libncursesw5-dev \
#     xz-utils tk-dev libffi-dev liblzma-dev python3-openssl
# RUN apt-get update && apt-get install -y postgresql-client
    

# # Установка pip и setuptools
# RUN python3 -m ensurepip && \
#     pip3 install --upgrade pip setuptools

# # Переходим в образе в директорию /app: в ней будем хранить код проекта.
# # Если директории с указанным именем нет, она будет создана. 
# # Название директории может быть любым.
# WORKDIR /app
# # Дальнейшие инструкции будут выполняться в директории /app

# # Скопировать с локального компьютера файл зависимостей
# # в текущую директорию (текущая директория — это /app).
# COPY requirements.txt .

# # Выполнить в текущей директории команду терминала
# # для установки зависимостей.
# RUN pip install -r requirements.txt --no-cache-dir

# # Скопировать всё необходимое содержимое 
# # той директории локального компьютера, где сохранён Dockerfile,
# # в текущую рабочую директорию образа — /app.
# COPY . .

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
# ////////////////////////////////////////////////////////////////////