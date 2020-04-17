''' 
    Модуль содержит класс LinksSaver, который извлекает домены из ссылок
    и сохраняет в БД Redis.
'''
import re
from datetime import datetime


class LinksSaver:
    '''
    Пример использования:
        links_saver = LinksSaver(data["links"], datetime.datetime.now(tz=tz), redis_instance)
        response = links_saver.save()
    
    Возвращает словарь {"status": "ok"}, если нет ошибок. 
    Если ошибки есть, {"status": "warning", description: "описание"} 
    или {"status": "error", description: "описание"} 
    '''

    def __init__(self, links_list, timestamp: datetime, redis_instance):
        self.links_list = links_list
        self.timestamp = timestamp
        self.redis_instance = redis_instance
        self.response = {"status": "ok"}
    
    def save(self):
        self.exctract_domains()
        self.remove_dublicates()
        self.save_to_redis()
        return self.response
    
    def exctract_domains(self):
        pattern = r"[a-z0-9\-_]{2,}\.[a-z]{2,4}"
        for index, link in enumerate(self.links_list):
            try:
                self.links_list[index] = re.search(pattern, link).group(0)
            except AttributeError:
                self.add_warning_about_bad_link(link)

    def add_warning_about_bad_link(self, link):
        msg = f"Warning! Link '{link}' has bad format and didn`t save to database! "
        self.response["status"] == "warning"
        if self.response["description"]:  
            self.response["description"] += msg
        else:
            self.response["description"] = msg

    def remove_dublicates(self):
        self.links_list = list(set(self.links_list))

    def save_to_redis(self):
        key = self.timestamp.isoformat().split('.')[0]
        try:
            self.redis_instance.lpush(key, *self.links_list)
        except Exception as e:
            self.response["status"] = "error"
            self.response["description"] = f"{e}"
