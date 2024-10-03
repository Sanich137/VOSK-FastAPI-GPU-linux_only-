from utils.pre_start_init import app
import logging
import datetime
from utils.states_machine import State
import os
import psutil


@app.get("/is_alive")
async def check_if_service_is_alive():
    """Перед направлением запроса, проверить наличие свободных мест. На практике, похоже, нормальная скорость
    обеспечивается при неболее чем 1 к 1 к количеству физических ядер процессора. """
    # Todo - запустить проверку сервиса - направить запрос и получить ответ. Сверить с ожидаемым ответом и, если ОК,
    #  Возвращать True
    logging.debug('GET_is_alive')
    logging.info(f'В работе {len(State.request_data)} задач')
    data = {"cpus": os.cpu_count(),
            "cpu_in_use": sum(1 for proc in psutil.process_iter() if proc.name() in ['python.exe', 'python']),
            "tasks_in_work": list(State.request_data.keys()),
            }

    if len(State.request_data.keys()) >= os.cpu_count():

        # sum(1 for proc in psutil.process_iter() if proc.name() == 'python.exe') >= os.cpu_count()): \
        # or (len(State.request_data.keys()) != 0):  # os.cpu_count():

        logging.debug(f'Задач перелимит, тормозим направление новых')
        closest_fin_time = datetime.datetime(3000, 1, 1, 00, 00, 00, 1)  # Увеличиваем в космос для
        logging.debug(f'Время стартовое -{closest_fin_time}')

        for task_id in State.request_data.keys():
            if State.request_data[task_id].get('work_till'):
                work_till = datetime.datetime.strptime(State.request_data[task_id].get('work_till'),
                                               "%Y-%m-%d %H:%M:%S.%f")
                if work_till < closest_fin_time:
                    closest_fin_time = datetime.datetime.strptime(State.request_data[task_id].get('work_till'),
                                               "%Y-%m-%d %H:%M:%S.%f")
            else:
                closest_fin_time = datetime.datetime.now()+datetime.timedelta(seconds=20)

            if closest_fin_time <= datetime.datetime.now()+datetime.timedelta(seconds=10):
                closest_fin_time = datetime.datetime.now()+datetime.timedelta(seconds=10)

        pause_to = closest_fin_time
    else:
        logging.debug(f'Процессов python меньше чем ядер, или нет ни одной задачи в работе. Можно наваливать работы ещё')
        pause_to = datetime.datetime.now()

    data['pause_to'] = pause_to

    return {"error": False,
            "error_description": None,
            "data": data}

# Версия от 23.08.2024
# @app.get("/is_alive")
# async def check_if_service_is_alive():
#     """
#     Не уверен, что нужная вещь. Пока всегда отдаёт, что ошибок нет.
#     """
#     # Todo - запустить проверку сервиса - направить запрос и получить ответ. Сверить с ожидаемым ответом и, если ОК,
#     #  Возвращать True
#     logging.debug('GET_check')
#     logging.info(f'В работе {len(State.request_data)} задач')
#
#     return {"error": False,
#             "error_description": None,
#             "data": State.request_data}
