import datetime

import pytest
import redis

from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .business_logic.links_saver import LinksSaver


redis_instance = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_NUMBER,
)


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


def test_get_all(api_client):
    url = reverse('api:all_items')
    response = api_client.get(url)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Testing "visited_links" endpoint


def test_post_links(api_client):
    redis_instance.flushdb()
    
    url = reverse('api:visited_links')
    tz = timezone.get_default_timezone()
    request_time = datetime.datetime.now(tz=tz)
    response = api_client.post(
        url,
        data={
            "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",
            ]
        },
        content_type='application/json',
    )

    assert response.status_code == 201
    check_saved_links_in_redis(request_time)

    # очистка БД
    redis_instance.flushdb()


def check_saved_links_in_redis(timestamp):
    # достаём из Редиса данные
    # формат ключа 2020-04-16T11:39:10
    key = timestamp.isoformat().split('.')[0]
    lenght_list = redis_instance.llen(key)

    assert lenght_list > 0
    for i in range(lenght_list):
        domain = redis_instance.lindex(key, i).decode("utf-8")
        assert domain in ["ya.ru", "funbox.ru", "stackoverflow.com"]


def test_save_links(api_client):
    redis_instance.flushdb()
    data = [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "funbox.ru",
        "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",        
    ]
    timestamp = datetime.datetime(2020, 4, 16, 12, 0, 0)
    response = LinksSaver(data, timestamp, redis_instance).save()

    assert response["status"] == "ok"
    check_saved_links_in_redis(timestamp)
    
    redis_instance.flushdb()


def test_save_bad_links(api_client):
    redis_instance.flushdb()
    data = [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "funboxru",
        "https://stackoverflowcom/questions/11828270/how-to-exit-the-vim-editor",        
    ]
    timestamp = datetime.datetime(2020, 4, 16, 12, 0, 0)
    response = LinksSaver(data, timestamp, redis_instance).save()

    assert response["status"] == "warning"

    redis_instance.flushdb()


@pytest.mark.parametrize('data', [
        "123",
        {"123": "123"},
        {"links": "123"},
    ])
def test_send_bad_json(data, api_client):
    url = reverse('api:visited_links')
    tz = timezone.get_default_timezone()
    request_time = datetime.datetime.now(tz=tz)
    response = api_client.post(
        url,
        data=data,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json()["status"] == "error" 
 

# ---------------------------------------------------------------------------
# Testing "visited_domains" endpoint


def test_get_visited_domains(api_client):
    redis_instance.flushdb()
    
    # первый тестовый список доменов
    timestamp1 = datetime.datetime(2020, 4, 16, 12, 0, 0)
    key1 = timestamp1.isoformat().split('.')[0]
    links_list = [
        "ya.ru",
        "mail.ru",
    ]
    redis_instance.lpush(key1, *links_list)

    # второй тестовый список доменов через 5 секунд
    timestamp2 = datetime.datetime(2020, 4, 16, 12, 0, 5)
    key2 = timestamp2.isoformat().split('.')[0]
    links_list = [
        "stackoverflow.com",
        "funbox.ru",
    ]
    redis_instance.lpush(key2, *links_list)

    url = reverse('api:visited_domains')
    response = api_client.get(url, {'from': key1, 'to': key2})
    domains = response.json()["domains"]

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    # множества должны быть одинаковыми, поэтому ^ даст пустое множество
    xor_set = set(domains) ^ set(["ya.ru","stackoverflow.com", "funbox.ru", "mail.ru"])
    assert bool(xor_set) == False

    redis_instance.flushdb()

def test_get_visited_domains_wrong_timestamp(api_client):
    url = reverse('api:visited_domains')
    response = api_client.get(url, {'from': '2020-04-17T12:44:01', 'to': '202ssssssT12:44:02'})

    assert response.status_code == 400
    assert response.json()["status"] == "error"


def test_get_visited_domains_required_paremeter_is_absent(api_client):
    url = reverse('api:visited_domains')
    response = api_client.get(url, {'from': '2020-04-17T12:44:01'})

    assert response.status_code == 400
    assert response.json()["status"] == "error"


# ---------------------------------------------------------------------------
# Testing additional endpoints

def test_clear(api_client):
    redis_instance.lpush("123", "qwe", "asd")
    url = reverse('api:clear')

    api_client.get(url)

    assert bool(redis_instance.keys("*")) == False


def test_gets_all_item(api_client):
    redis_instance.lpush("123", "qwe", "asd")
    url = reverse('api:all_items')

    response = api_client.get(url)

    assert response.json()['count'] == 1
