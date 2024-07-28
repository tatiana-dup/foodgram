## Описание проекта:

Этот проект представляет собой сайт для публикации рецептов.
Пользователи могут просматривать рецепты и страницы других пользователей. Рецепты можно фильтровать по тегам.
Авторизованные пользователи могут создавать собственные рецепты, добавлять любые рецепты в избранное, а также список покупок, который можно скачать в формате txt (в файле будет список ингредиентов необходимых для рецептов из списка покупок). Авторизованные пользователи могут подписываться на других пользователей, просматривать список своих подписок, а также изменять и удалять собственные рецепты.
Администратор через админ-зону может создавать новые теги и ингредиенты.

В бэкенде проекта использованы: Python3.9, Django, Django REST Framework, SQLite3.
Аутентификация пользователей настроена по токену аутентификации с использованием Djoser.
Проект подготовлен для запуска в контейнерах с использованием Docker, GitHub Actions и Nginx.


## Документация API:
При локальном запуске проекта статическая документация для API доступна по адресу: http://127.0.0.1:7000/api/docs/


## Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:tatiana-dup/foodgram.git
```

```
cd foodgram/
```

Установить Docker:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```

На основе .env.example создать собственный файл .env с переменными окружения.

Собрать образы и отправить их в Docker Hub, заменив username на нужный:
```
cd frontend
docker build -t username/foodgram_frontend .
docker push username/foodgram_frontend
cd ../backend
docker build -t username/foodgram_backend .
docker push username/foodgram_backend
cd ../infra
docker build -t username/foodgram_gateway .
docker push username/foodgram_gateway
```

В файле docker-compose.production.yml укажите нужные образы.

Для запуска проекта в контейнерах выполнить команду:
```
docker compose -f docker-compose.production.yml up -d
```

После запуска контейнеров выполните миграции и соберите статику:
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
docker compose -f docker-compose.production.yml exec backend python manage.py import_csv

```

Приложение должно быть доступно по адресу http://localhost:7000.



## Примеры запросов:

### Получение всех рецептов
```
GET /api/recipes/
```

### Создание рецепта
```
POST /api/recipes/
Content-Type: application/json
{
    "text": "string",
    "image": "string",
    "group": 0
}
```

### Получение рецепта
```
GET /api/v1/posts/{id}/
```

### Получение всех подписок пользователя
```
GET /api/v1/follow/
```

### Подписка пользователя на другого
```
POST /api/v1/follow/
Content-Type: application/json
{
    "following": "string"
}
```

---
Автор проекта: [Татьяна Дуплинская](https://github.com/tatiana-dup)