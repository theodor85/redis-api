import datetime

import pytest
import redis

from django.urls import reverse
from django.conf import settings

from .business_logic.links_saver import save_links


redis_instance = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_TEST_DB,
)


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


# def test_get_all(api_client):
#     url = reverse('api:all_items')
#     response = api_client.get(url)
#     assert response.status_code == 200

def test_post_links(api_client):
    url = reverse('api:visited_links')
    request_time = datetime.datetime.now()
    response = api_client.post(url, {
        "links": [
           "https://ya.ru",
           "https://ya.ru?q=123",
           "funbox.ru",
           "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",
        ]
    })

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

    data = [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "funbox.ru",
        "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",        
    ]
    timestamp = datetime.datetime(2020, 4, 16, 12, 0, 0)
    save_links(data, timestamp, redis_instance)

    check_saved_links_in_redis(timestamp)

