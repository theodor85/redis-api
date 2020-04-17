## Описание

REST веб-сервис на Django + Django Rest Framework. В качестве основной базы данных - Redis

## Запуск системы

```
git clone https://github.com/theodor85/redis-api.git
cd redis-api
docker-compose up
```

## Запуск тестов

```
docker-compose run --rm django pytest
```

## Endpoints

### Основные

```
POST /visited_links/
```
Отправляет в формате JSON данные и сохраняет в БД домены и время их сохранения.


```
GET /visited_domains?from=2020-04-16T11:39:40&to=2020-04-16T11:39:40
```
Получает домены, сохраненные за указанный промежуток времени.
Формат даты - строка вида "2020-04-16T11:39:10". 
Такую строку можно получить так: 
```
datetime_variable.isoformat().split('.')[0],
```
т.е. путем отрезания миллисекунд от isoformat.

### Дополнительные (для удобства отладки)

```
GET /all/
```
Возвращает список всех сохраенных элементов.
```
GET /clear/
```
Очищает базу данных.