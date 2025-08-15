# //////////////////PRODUCTION CONTAINER////////////////////////
# FROM nginx:latest

# # Создаем директорию для сертификатов
# RUN mkdir -p /etc/letsencrypt/live/

# # Копируем основной конфиг Nginx
# COPY nginx.conf /etc/nginx/nginx.conf

# # Копируем конфиг server block
# COPY default.conf /etc/nginx/conf.d/default.conf

# # Настраиваем права доступа
# RUN chown -R nginx:nginx /etc/letsencrypt
# ////////////////////////////////////////////////////////////