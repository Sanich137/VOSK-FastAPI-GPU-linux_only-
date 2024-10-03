from config import buffer_size
import uuid
from datetime import datetime as dt


class StateAudioClassifier:
    def __init__(self):
        self.request_limit = buffer_size
        self.request_data = dict()
        # todo - сейчас все данные для ответов тоже складываются в self.request_data, а должны в self.response_data,
        #  переделать
        self.response_data = dict()

    def reg_new_request(self, file_url, classificate_variants, erp_file_id, do_lawyer_text_description, do_analysis_of_sales_communication,
                        do_quality_analysis_of_lawyer_communication) -> dict:
        """
        Errors_list:
        0 - Отсутствует ошибка
        1 - Достигнут предел по количеству задач в работе одновременно.
        2 - Файл уже направлялся на распознавание ранее
        3 - Ошибка функции проверки нахождения задачи в работе
        """
        unique_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(file_url) + str(erp_file_id)))
        error = "3"
        error_description = None
        data = None

        # Проверить количество возможных запросов в буфере
        if len(self.request_data) > self.request_limit:
            error = "1"
            error_description = f"Reached buffer limit in {buffer_size} tasks"
        # Проверить есть ли в реестре
        else:
            if unique_id in self.request_data.keys():
                error = "2"
                error_description = "Order already proceeded to tasks list"
            else:
                error = "0"

        # добавить в реестр
        if error == "0":
            self.request_data[unique_id] = dict(
                    task_id=unique_id,
                    file_url=file_url,
                    variants=classificate_variants,
                    erp_file_id=erp_file_id,
                    start_date=dt.now(),
                    do_lawyer_text_description=do_lawyer_text_description,
                    do_analysis_of_sales_communication=do_analysis_of_sales_communication,
                    do_quality_analysis_of_lawyer_communication=do_quality_analysis_of_lawyer_communication,
                    state="new"
            )
            self.response_data[unique_id] = dict(
                    state="new",
                    task_id=unique_id,
                    duration=float(),
                    cat_ids=list(),
                    cat_names=list(),
                    raw_recognition=list(),
                    sentenced_recognition=list(),
            )

            data = unique_id

        # отдать номер заявки
        return {
            "error": error,
            "error_description": error_description,
            "data": data
        }


State = StateAudioClassifier()