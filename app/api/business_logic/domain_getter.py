import datetime
import re


def get_domains(from_: str, to: str, redis_instance):
    '''
        from_, to:  строка вида "2020-04-16T11:39:10". 
                Такую строку можно получить так: datetime_variable.isoformat().split('.')[0],
                т.е. путем отрезания миллисекунд от isoformat
    '''
    domains = list()
    result = {
        "domains": domains,
    }

    try_to_get_time_range(from_, to, redis_instance, result)

    # устраняем дубликаты
    result["domains"] = list(set( result["domains"] ))

    return result


def try_to_get_time_range(from_, to, redis_instance, result):
    try:
        for time_key in TimeRange(from_, to):
            list_length = redis_instance.llen(time_key)
            for i in range(list_length):
                result["domains"].append( redis_instance.lindex(time_key, i) )
    except WrongTimestampFormat as e:
        result.update({"status": e.message})


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

