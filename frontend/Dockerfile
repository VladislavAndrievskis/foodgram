# ================== ФРОНТЕНД (React) ==================
# Используем Node 16 — стабильная версия для Create React App
FROM node:16-alpine AS builder

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости с игнорированием peer-конфликтов
RUN npm install --legacy-peer-deps

# Копируем исходники
COPY . .

# Удаляем кэш и пересобираем (на всякий случай)
RUN npm cache verify

# Сборка с отключённой строгой проверкой (на случай ошибок в CI)
ENV CI=false

# Запускаем сборку
RUN npm run build

# Этап 2: Сервинг через Nginx
FROM nginx:alpine

# Копируем кастомный конфиг (опционально)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные файлы из builder
COPY --from=builder /app/build /usr/share/nginx/html

# Открываем порт
EXPOSE 80

# Запускаем Nginx
CMD "nginx", "-g", "daemon off;"
