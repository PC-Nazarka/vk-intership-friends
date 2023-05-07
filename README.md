# Friends

## Инструкция по запуску

Запустите контейнера
```bash
docker-compose up -d --build
```

Примените миграции
```bash
docker-compose run django python manage.py migrate
```

После предыдущих действий у нас будет работать сервер по адресу http://localhost:8000

## Тесты

Для запуска тестов нужно (необязательно) установить на локальную машину библиотеки
```bash
pip install invoke rich
```

Для тестов обязательно применить миграции.

Запуск тестов
```bash
inv tests.pytest
```

Альтернативный запуск тестов
```bash
docker-compose run --rm django pytest
```

## Линтеры

Для запуска линтеров нужно (необязательно) установить на локальную машину библиотеки
```bash
pip install invoke rich
```

Запуск линтеров
```bash
inv linters.all
```

Альтернативный запуск линтеров
```bash
docker-compose run --rm django flake8 . --config=./setup.cfg
docker-compose run --rm django isort . --settings-file=./setup.cfg
```

## OpenAPI

В директории docs присутствует файл openapi.yml

В docker-compose присутствует сервис для чтения и редактирования документации, который запущен на http://localhost:8080/

Копируем все из файла и вставляем в сервисе в поле для редактирования. После можем видеть
список API методов.


## Примеры использования API

Запрос №1

```
Request:
Адрес: http://localhost:8000/api/users/
Метод: POST
Тело:
{
    "username": "name",
    "first_name": "",
    "last_name": "",
    "password": "123"
}

Response:
Статус ответа: 201
Тело ответа:
{
    "id": 1,
    "username": "name",
    "first_name": "",
    "last_name": ""
}
```

Запрос №2

```
Request:
Адрес: http://localhost:8000/api/token/
Метод: POST
Тело: {
    "username": "name",
    "password": "123"
}

Response:
Статус ответа: 200
Тело ответа:
{
    "refresh": "some_refresh_token",
    "access": "some_access_token"
}
```

Запрос №3

```
Request:
Адрес: http://localhost:8000/api/token/refresh/
Метод: POST
Тело:
{
    "refresh": "some_refresh_token"
}

Response:
Статус ответа: 200
Тело ответа:
{
    "refresh": "some_refresh_token",
    "access": "some_access_token"
}
```

Запрос №4

```
Request:
Адрес: http://localhost:8000/api/users/
Метод: GET
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
[
    {
        "id": 1,
        "username": "name",
        "first_name": "",
        "last_name": ""
    },
    {
        "id": 2,
        "username": "name1",
        "first_name": "",
        "last_name": ""
    }
]
```

Запрос №5

```
Request:
Адрес: http://localhost:8000/api/users/1/
Метод: GET
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
{
    "id": 1,
    "username": "name",
    "first_name": "",
    "last_name": ""
}
```

Запрос №6

```
Request:
Адрес: http://localhost:8000/api/users/incoming-invites/
Метод: GET
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
[]
```

Запрос №7

```
Request:
Адрес: http://localhost:8000/api/users/outgoing-invites/
Метод: GET
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
[
    {
        "id": 1,
        "target": {
            "id": 2,
            "username": "name1",
            "first_name": "",
            "last_name": ""
        },
        "is_accept": null,
        "owner": {
            "id": 1,
            "username": "name",
            "first_name": "",
            "last_name": ""
        }
    }
]
```

Запрос №8

```
Request:
Адрес: http://localhost:8000/api/users/friends/
Метод: GET
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
[
    {
        "id": 2,
        "username": "name1",
        "first_name": "",
        "last_name": ""
    }
]
```

Запрос №9

```
Request:
Адрес: http://localhost:8000/api/users/2/status/
Метод: GET
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
{
    "status": "Уже друзья"
}
```

Запрос №10

```
Request:
Адрес: http://localhost:8000/api/users/2/delete-friend/
Метод: DELETE
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 204
```

Запрос №11

```
Request:
Адрес: http://localhost:8000/api/invites/
Метод: POST
Тело:
{
    "target": 2
}
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 201
Тело ответа:
{
    "id": 1,
    "target": {
        "id": 2,
        "username": "name1",
        "first_name": "",
        "last_name": ""
    },
    "is_accept": null,
    "owner": {
        "id": 1,
        "username": "name",
        "first_name": "",
        "last_name": ""
    }
}
```

Запрос №12

```
Request:
Адрес: http://localhost:8000/api/invites/1/
Метод: GET
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
{
    "id": 1,
    "target": {
        "id": 2,
        "username": "name1",
        "first_name": "",
        "last_name": ""
    },
    "is_accept": true,
    "owner": {
        "id": 1,
        "username": "name",
        "first_name": "",
        "last_name": ""
    }
}
```

Запрос №13

```
Request:
Адрес: http://localhost:8000/api/invites/1/accept/
Метод: PATCH
Тело:
{
    "is_accept": true
}
Заголовки:
Authorization: JWT some_access_token

Response:
Статус ответа: 200
Тело ответа:
{
    "message": "Статус заявки изменен"
}
```
