# ================== ФРОНТЕНД (React/Vue) ==================
# Этап 1: Сборка
FROM node:16-alpine AS builder

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install --force



# Копируем исходники
COPY . .

# Сборка проекта
RUN npm run build

# Этап 2: Сервинг через Nginx
FROM nginx:alpine

# Копируем кастомный конфиг (опционально, можно в docker-compose)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные файлы из builder
COPY --from=builder /app/build /usr/share/nginx/html

# Открываем порт
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
# # Используем образ с Node.js
# FROM node:18-alpine

# # Рабочая директория в контейнере
# WORKDIR /app

# # Копируем package.json и устанавливаем зависимости
# COPY package.json .

# RUN npm install

# # Копируем исходники
# COPY . .

# # Собираем проект
# RUN npm run build

# # Устанавливаем serve для раздачи статики
# RUN npm install -g serve

# # Запускаем сервер
# CMD ["serve", "-s", "build", "-l", "3000"]
