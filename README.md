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
Адрес: http://localhost:8000/api/token/
Метод: POST

Статус ответа:
Тело ответа:
```

Запрос №2

```
Адрес: http://localhost:8000/api/token/refresh/
Метод: POST

Статус ответа:
Тело ответа:
```

Запрос №3

```
Адрес: http://localhost:8000/api/users/
Метод: POST
Тело:

Статус ответа:
Тело ответа:
```

Запрос №4

```
Адрес: http://localhost:8000/api/users/
Метод: GET

Статус ответа:
Тело ответа:
```

Запрос №5

```
Адрес: http://localhost:8000/api/users/<int:pk>/
Метод: GET

Статус ответа:
Тело ответа:
```

Запрос №6

```
Адрес: http://localhost:8000/api/users/incoming-invites/
Метод: GET

Статус ответа:
Тело ответа:
```

Запрос №7

```
Адрес: http://localhost:8000/api/users/outgoing-invites/
Метод: GET

Статус ответа:
Тело ответа:
```

Запрос №8

```
Адрес: http://localhost:8000/api/users/friends/
Метод: GET

Статус ответа:
Тело ответа:
```

Запрос №9

```
Адрес: http://localhost:8000/api/users/<int:pk>/friend-status/
Метод: GET

Статус ответа:
Тело ответа:
```

Запрос №10

```
Адрес: http://localhost:8000/api/users/<int:pk>/delete-friend/
Метод: DELETE

Статус ответа:
Тело ответа:
```

Запрос №11

```
Адрес: http://localhost:8000/api/invites/
Метод: POST

Статус ответа:
Тело ответа:
```

Запрос №12

```
Адрес: http://localhost:8000/api/invites/<int:pk>/
Метод: GET

Статус ответа:
Тело ответа:
```

Запрос №13

```
Адрес: http://localhost:8000/api/invites/<int:pk>/accept/
Метод: PATCH

Статус ответа:
Тело ответа:
```
