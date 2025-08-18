[![Main FOODGRAM workflow](https://github.com/VladislavAndrievskis/foodgram/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/VladislavAndrievskis/foodgram/actions/workflows/foodgram_workflow.yml)
# "Продуктовый помощник" (Foodgram)
---
## Описание <a id=1></a>

Проект "Продуктовый помошник" (Foodgram) предоставляет пользователям следующие возможности:
  - регистрироваться
  - создавать свои рецепты и управлять ими (корректировать\удалять)
  - просматривать рецепты других пользователей
  - добавлять рецепты других пользователей в "Избранное" и в "Корзину"
  - подписываться на других пользователей
  - скачать список ингредиентов для рецептов, добавленных в "Корзину"
---
### Описание проекта

**Foodgram** — это проект, разработанный в рамках финального задания спринта №18. Проект направлен на повторение навыков бэкэнд рзрботки, настройки и запуска проектов в контейнерах, а также настройки автоматического тестирования и деплоя на удалённый сервер.

### Стек технологий

* **Python 3.12**
* **Django 4.2**
* **gunicorn 20.1.0**
* **PyYAML 6.0**
* **djoser 2.1.0**
* **djangorestframework 3.16**
* **Pillow 11.3.0**

### Настройка и запуск

1. **Форкните репозиторий**: [VladislavAndrievskis/kittygram_final](https://github.com/VladislavAndrievskis/Foodgram.git)
2. **Клонируйте репозиторий** на свой компьютер
3. **Настройте секреты** в GitHub:
   * В настройках репозитория перейдите в **Secrets and variables/actions**
   * Добавьте следующие секреты:
     * **DOCKER_PASSWORD** и **DOCKER_USERNAME** (логин и пароль от Docker.com)
     * **HOST**, **SSH_KEY**, **USER**, **SSH_PASSPHRASE** (данные удалённого сервера)
     * **TELEGRAM_TO** и **TELEGRAM_TOKEN** (для уведомлений в Telegram)

### Настройка окружения

1. На сервере создайте директорию **Foodgram**
2. В директории создайте файл **.env** и определите:
   * **SECRET_KEY**

### Автотесты

Для локального запуска тестов:
1. Создайте виртуальное окружение
2. Установите зависимости:
   ```bash
   pip install -r backend/Foodgram/requirements.txt
   ```
3. Запустите тесты:
   ```bash
   pytest
   ```
### Примеры использования
### Эндпоинты

* **Регистрация**: https://andrievskis.sytes.net/signup
* **Авторизация**: https://andrievskis.sytes.net/signin
* **Главная страница**: https://andrievskis.sytes.net/recipes
* **Создть рецепт**: https://andrievskis.sytes.net/recipes/create

### Авторы

* **Команда Яндекс Практикума** [yandex-praktikum](https://github.com/yandex-praktikum)
* **Владислав Андриевскис** [VladislavAndrievskis](https://github.com/VladislavAndrievskis)

### Админкa
admin
admin
