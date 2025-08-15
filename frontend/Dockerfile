# //////////////////PRODUCTION CONTAINER////////////////////////
# FROM node:18 as builder

# WORKDIR /app

# # Копируем package.json и устанавливаем зависимости
# COPY package.json package-lock.json ./
# RUN npm ci --force

# # Копируем исходники
# COPY . .

# # Устанавливаем PUBLIC_URL=/ (чтобы пути были /static/css/, /static/js/)
# ENV PUBLIC_URL=/

# # Собираем
# RUN npm run build

# # Финальный образ — просто копируем build
# FROM alpine:latest
# WORKDIR /app/build
# COPY --from=builder /app/build .
# ////////////////////////////////////////////////////////////////