'''  '''
import re


def save_links(links_list, timestamp, redis_instance):
    exctract_domains(links_list)
    remove_duplicates(links_list)
    save_to_redis(links_list, timestamp, redis_instance)

def exctract_domains(links_list):
    # TODO: Допустимые символы в url: цифры [0-9], латиница в нижнем регистре [a-z], 
    # точка[.], слеш [/], дефис [-], нижнее подчеркивание [_]
    pattern = r"[a-z]{2,}\.[a-z]{2,4}"
    for index, link in enumerate(links_list):
        links_list[index] = re.search(pattern, link).group(0)

def remove_duplicates(links_list):
    links_list = list(set(links_list))

def save_to_redis(links_list, timestamp, redis_instance):
    key = timestamp.isoformat().split('.')[0]
    redis_instance.lpush(key, *links_list)
