from pydantic import BaseModel, HttpUrl
from typing import Union, Annotated
from config import port


class WebSocketModel(BaseModel):
    """OpenAPI не хочет описывать WS, а я не хочу изучать OPEN API. По этому описание тут.
    \n Подключение на порт: 49152
    \n На вход жду поток binary, buffer_size = 6400, mono, wav.
    \n На вход я должен получить словарь =
    \n  {text: '{ "config" : { "sample_rate" : any(int/float), "wait_null_answers": Bool}}'}
    \n (значение по ключу text - строка. мне удобнее получать json, но на тестовом стенде не завелось)
    \n На тестах почему-то процесс не отрабатывает при "wait_null_answers": False - не разбирался. Сокет в этом случае преждевременно  закрывается, сервис работу продолжает. Данные получаются не полные!
    \n Далее сообщения с данными {"bytes": binary} - словарь
    \n По окончании передачи {text: '{ "eof" : 1}'}
    \n
    """
    text: str