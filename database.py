import redis
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
from telegram.ext import CallbackContext


TODAY = datetime.today().date().isoformat()

redis_moon_info: redis.Redis = redis.Redis(db=1)
redis_user_info: redis.Redis = redis.Redis(db=2)

def set_moon_data(context: CallbackContext = None) -> None:
    '''Used for getting data from site and 
    pass it into redis using datetime.today() as a key'''

    site_url = 'https://mirkosmosa.ru/lunar-calendar/phase-moon/lunar-day-today'
    request_url =  requests.request('GET', site_url)
    soup: list = [tag.text.strip() for tag in bs(request_url.text, 'html.parser').find_all('div', 'div_table')]
    for text_block in soup: 
        redis_moon_info.rpush(TODAY, text_block)
        print(text_block[0])

def get_moon_data() -> dict:
    '''Used for getting data from redis and convert it to a python dict'''

    len_moon_data: int = redis_moon_info.llen(TODAY)
    redis_request = redis_moon_info.lrange(TODAY, 0, len_moon_data)
    redis_list: list = [item.decode('utf-8') for item in redis_request]
    python_dict: dict = {item.split('\n')[0]: item for item in redis_list}
    return python_dict

def set_user_info(user_id: str, time: str) -> None:
    redis_user_info.set(user_id, time)

def get_user_info(user_id: str) -> str:
    if user := redis_user_info.get(user_id): 
        return user.decode('utf-8')
    return ''
