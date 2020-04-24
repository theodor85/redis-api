'''
    Модуль содержит класс DomainGetter, который отдаёт список доменов, 
    посещенных за заданный временной промежуток
'''

import datetime
import re


class DomainGetter:
    '''
        from_, to:  строка вида "2020-04-16T11:39:10". 
                Такую строку можно получить так: datetime_variable.isoformat().split('.')[0],
                т.е. путем отрезания миллисекунд от isoformat
        Пример использования:
            response = DomainGetter(from_, to, redis_instance).get()
    
        Возвращает словарь {"status": "ok"}, если нет ошибок. 
        Если ошибки есть, {"status": "warning", description: "описание"} 
        или {"status": "error", description: "описание"} 
    '''
    def __init__(self, from_: str, to: str, redis_instance=None):
        self.verify_timeformat(from_)
        self.verify_timeformat(to)
        self.from_ = from_
        self.to = to
        self.redis_instance = redis_instance
        self.response = {"status": "ok"}
    
    def get(self):
        domains = list()
        self.response.update({
                "domains": domains,
        })
        self.try_to_get_values_from_time_range()
        # устраняем дубликаты
        self.response["domains"] = list(set( self.response["domains"] ))

        return self.response

    @staticmethod
    def verify_timeformat(str_timestamp):
        if not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$", str_timestamp): 
            raise WrongTimestampFormat("Timestamp string must be in '2020-04-16T11:00:00' format! ")

    def try_to_get_values_from_time_range(self):
        # сделать маску, по которой получать ключи
        mask = self.get_mask(self.from_, self.to)
        for key in self.redis_instance.keys(mask):
            list_length = self.redis_instance.llen(key)
            for i in range(list_length):
                self.response["domains"].append( self.redis_instance.lindex(key, i) )

    @staticmethod
    def get_mask(from_, to):
        mask = ''
        for i in range(len(from_)):
            if from_[i] == to[i]:
                mask += from_[i]
            else:
                mask += '*'
                break
        return mask


class WrongTimestampFormat(Exception):
    pass

