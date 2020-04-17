import datetime
import json
from json.decoder import JSONDecodeError

import redis
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .business_logic.links_saver import LinksSaver
from .business_logic.domain_getter import DomainGetter


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
    response = {"status": "ok"}
    data = try_to_load_json(request)
    
    if data:
        tz = timezone.get_default_timezone()
        timestamp = datetime.datetime.now(tz=tz)
        response = LinksSaver(data["links"], timestamp, redis_instance).save()
    else:
        response.update(
            {
                "status": "error",
                "descripton": "An error has happened!It may be 3 reasons: 1) wrong JSON format, 2) there is no 'links' key and 3) data['links'] is no list",
            }
        )
        return Response(response, status=400)

    if response["status"] == "error":
        return Response(response, status=400)
    return Response(response, status=201)

def try_to_load_json(request):
    try:
        data = json.loads( request.body.decode("utf-8").replace("\'", "\"") )
        if not isinstance(data["links"], list):
            return None
    except (JSONDecodeError, TypeError, KeyError):
        return None
    return data


@api_view(['GET'])
def visited_domains(request, *args, **kwargs):
    response = {"status": "ok"}
    status = 200

    try:
        from_ = request.GET["from"]
        to = request.GET["to"]
    except KeyError:
        response["status"] = "error"
        response["description"] = "Wrong request format! Request must be 'visited_domains/?from=2020-04-17T10:54:17&to=2020-04-17T10:55:58'"
        status = 400
        return Response(response, status=status)

    response = DomainGetter(from_, to, redis_instance).get()

    if response["status"] != "ok":
        status = 400
    return Response(response, status=status)
