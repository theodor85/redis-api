import datetime
import json

import redis
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .business_logic.links_saver import save_links


# Connect to our Redis instance
redis_instance = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_MAIN_DB,
)


@api_view(['GET'])
def all_items(request):
    if request.method == 'GET':
        items = {}
        count = 0
        for key in redis_instance.keys("*"):
            items[key.decode("utf-8")] = redis_instance.get(key)
            count += 1
        response = {
            'count': count,
            'msg': f"Found {count} items.",
            'items': items
        }
        return Response(response, status=200)


@api_view(['POST'])
def visited_links(request, *args, **kwargs):
    print('************************************')
    print(request.body)
    
    
    data = json.loads( request.body )
    
    
    
    save_links(data["links"], datetime.datetime.now(), redis_instance)
    response = {"status": "ok"}
    return Response(response, status=201)
