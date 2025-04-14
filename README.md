# Продуктовый помощник Foodgram 

## Описание проекта 

«Фудграм» — веб-приложение, в котором
пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное
и подписываться на публикации других авторов. Зарегистрированным пользователям
также будет доступен сервис «Список покупок». Он позволит создавать список
продуктов, которые нужно купить для приготовления выбранных блюд.

## Запуск проекта

Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:

```bash
git clone https://github.com/Aleksandra255685/foodgram-st
```

- Создайте файл .env в папке проекта:
```.env
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
POSTGRES_DB=django

DB_HOST=db
DB_PORT=5432

SECRET_KEY = ' '
ALLOWED_HOSTS="127.0.0.1 localhost"
```

- Выполните команду сборки контейнеров:
```bash
# foodgram-st
docker compose up --build
```

- Выполните миграции:
```bash
docker compose exec backend python manage.py migrate
```
- Создайте суперпользователя:
```bash
docker compose exec backend python manage.py createsuperuser
```
-  Заполните базу тестовыми данными:
```bash
docker compose exec backend python manage.py loaddata db.json
```
- Загрузите статику:
```bash
docker compose exec backend python manage.py collectstatic --no-input
```
### Основные адреса:
| Адрес               | Описание              |
|:--------------------|:----------------------|
| 127.0.0.1:8000      | Главная страница      |
| 127.0.0.1:8000/admin/    | Панель администратора |
| 127.0.0.1:8000/api/docs/ | API проекта           |
### Автор проекта
Венатовская Александра 