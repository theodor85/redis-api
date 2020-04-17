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
    def __init__(self, from_: str, to: str, redis_instance):
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

    def try_to_get_values_from_time_range(self):
        try:
            for time_key in TimeRange(self.from_, self.to):
                list_length = self.redis_instance.llen(time_key)
                for i in range(list_length):
                    self.response["domains"].append( self.redis_instance.lindex(time_key, i) )
        except WrongTimestampFormat as e:
            self.response.update({
                "status": "error",
                "description": str(e),
            })


class TimeRange:
    '''
        Итератор, отдающий последовательность строковых ключей вида 
        "2020-04-16T11:39:10" с точностью до секунды
    '''
    def __init__(self, from_: str, to: str):
        self.init_time = self.parse_time_stamp(from_)
        self.end_time = self.parse_time_stamp(to)
        self.delta = datetime.timedelta(seconds=1)
        self.current_time = self.init_time - self.delta

    def __iter__(self):
        return self

    def __next__(self):
        self.current_time += self.delta
        if self.current_time > self.end_time:
            raise StopIteration()
        return self.current_time.isoformat().split('.')[0]
    
    def parse_time_stamp(self, str_timestamp):
        self.verify_timeformat(str_timestamp)

        date_ = str_timestamp.split('T')[0]
        time_ = str_timestamp.split('T')[1]

        year = int( date_.split('-')[0] )
        month = int( date_.split('-')[1] )
        day = int( date_.split('-')[2] )

        hours = int( time_.split(':')[0] )
        minutes = int( time_.split(':')[1] )
        seconds = int( time_.split(':')[2] )

        return datetime.datetime(year, month, day, hours, minutes, seconds)
    
    def verify_timeformat(self, str_timestamp):
        if not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$", str_timestamp): 
            raise WrongTimestampFormat("Timestamp string must be in '2020-04-16T11:00:00' format! ")


class WrongTimestampFormat(Exception):
    pass

