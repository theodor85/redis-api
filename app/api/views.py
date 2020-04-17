import datetime
import json

import redis
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .business_logic.links_saver import save_links
from .business_logic.domain_getter import get_domains


# Connect to our Redis instance
redis_instance = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_NUMBER,
)


@api_view(['GET'])
def all_items(request):
    if request.method == 'GET':
        items = {}
        count = 0
        for key in redis_instance.keys("*"):

            lenght_list = redis_instance.llen(key)
            items[key.decode("utf-8")] = list()
            for i in range(lenght_list):
                items[key.decode("utf-8")].append( redis_instance.lindex(key, i) )
            count += 1
        response = {
            'count': count,
            'msg': f"Found {count} items.",
            'items': items
        }
        return Response(response, status=200)


@api_view(['GET'])
def clear(request):
    redis_instance.flushdb()
    return Response({"status": "ok"}, status=200)


@api_view(['POST'])
def visited_links(request, *args, **kwargs):
    data = json.loads( request.body.decode("utf-8").replace("\'", "\"") )
    
    tz = timezone.get_default_timezone()
    timestamp = datetime.datetime.now(tz=tz)

    save_links(data["links"], timestamp, redis_instance)
    response = {"status": "ok"}
    return Response(response, status=201)


@api_view(['GET'])
def visited_domains(request, *args, **kwargs):
    data = get_domains(request.GET["from"], request.GET["to"], redis_instance)
    response = {"status": "ok"}
    response.update(data)
    status = 200
    if response["status"] != "ok":
        status = 400
    return Response(response, status=status)
