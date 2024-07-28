## Описание проекта:

Этот проект представляет собой сайт для публикации рецептов.
Пользователи могут просматривать рецепты и страницы других пользователей. Рецепты можно фильтровать по тегам.
Авторизованные пользователи могут создавать собственные рецепты, добавлять любые рецепты в избранное, а также список покупок, который можно скачать в формате txt (в файле будет список ингредиентов необходимых для рецептов из списка покупок). Авторизованные пользователи могут подписываться на других пользователей, просматривать список своих подписок, а также изменять и удалять собственные рецепты.
Администратор через админ-зону может создавать новые теги и ингредиенты.

В бэкенде проекта использованы: Python3.9, Django, Django REST Framework, SQLite3.
Аутентификация пользователей настроена по токену аутентификации с использованием Djoser.
Проект подготовлен для запуска в контейнерах с использованием Docker, GitHub Actions и Nginx.


## Документация API:
При локальном запуске проекта статическая документация для API доступна по адресу: http://127.0.0.1/api/docs/


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
docker build -t username/taski_frontend .
docker push username/taski_frontend
cd ../backend
docker build -t username/taski_backend .
docker push username/taski_backend
cd ../gateway
docker build -t username/taski_gateway .
docker push username/taski_gateway
```

В файле docker-compose.production.yml укажите нужные образы.

Для запуска проекта в контейнерах ыполнить команду:
```
docker compose -f docker-compose.production.yml up
```



## Примеры запросов:

### Получение всех публикаций
```
GET /api/v1/posts/
```

### Создание публикации
```
POST /api/v1/posts/
Content-Type: application/json
{
    "text": "string",
    "image": "string",
    "group": 0
}
```

### Получение публикации
```
GET /api/v1/posts/{id}/
```

### Получение всех комментариев к публикации
```
GET /api/v1/posts/{post_id}/comments/
```

### Добавление комментария к публикации
```
POST /api/v1/posts/{post_id}/comments/
Content-Type: application/json
{
    "text": "string"
}
```

### Получение комментария
```
GET /api/v1/posts/{post_id}/comments/{id}/
```

### Получение всех сообществ
```
GET /api/v1/groups/
```

### Информация о сообществе
```
GET /api/v1/groups/{id}/
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