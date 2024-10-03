# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import statistics
import ujson  # работа с json-файлами и json-строками

from pydub import AudioSegment

from vosk import KaldiRecognizer

from models.vosk_model import vosk_model

from utils.pre_start_init import paths
from utils.states_machine import State


def offline_recognition(is_async=False, task_id=None, file_name=None):
    # Заводим переменные для сбора результата
    error = True
    error_description = None
    sound_duration = None
    raw_recognition = []
    sentenced_recognition = []
    text_only = []

    time_rec_start = datetime.now()
    # file_path = BASE_DIR/'content'/'2723.mp3'

    if is_async:
        file_name = State.request_data[task_id].get("file_url").path.split('/')[-1]
    if not file_name:
        logging.error("Не получено имя файла")
        error_description = "Не получен файл для распознавания"
    else:
        file_path = paths.get('trash_folder') / file_name
        "https://lk-office.amulex.ru/records/OUT.2023/06/29/20/4723.1688060830.33084.mp3"

        try:
            sound = AudioSegment.from_file(str(file_path))
        except Exception as e:
            print(e)
        else:
            sound_duration = sound.duration_seconds
            if sound:
                logging.debug(f'Файл принят в работу {file_name}')
                if int(sound_duration) < 5:
                    result = {"error": "No_audio_data",
                              "duration": sound_duration,
                              }
                elif int(sound_duration) > 42400:
                    result = {"error": "Duration_too_large",
                              "duration": sound_duration,
                              }
                else:
                    logging.debug(f'Общая продолжительность аудиофайла {sound_duration} сек.')
                    # Фреймрейт на входе
                    logging.debug(f'Исходный фреймрейт аудио - {sound.frame_rate}')
                    # Меняем фреймрейт на 16кГц
                    sound = sound.set_frame_rate(16000)
                    logging.debug(f'Изменённый фреймрейт аудио - {sound.frame_rate}')
                    # Разбиваем звук по каналам
                    separate_channels = sound.split_to_mono()
                    channels = sound.channels

                    for channel in range(channels):
                        offline_recognizer = None
                        offline_recognizer = KaldiRecognizer(vosk_model, sound.frame_rate)
                        offline_recognizer.SetWords(enable_words=True)
                        logging.debug(f'Передаём аудио на распознавание канал № {channel + 1}')

                        # Основная функция - можно сделать с разбивкой на сэмплы (возможно, уменьшает нагрузку на ОЗУ)
                        try:
                            logging.debug(f"Ждём распознавания")

                            offline_recognizer.AcceptWaveform(separate_channels[channel].raw_data)
                            # Далее только для Батчмодель
                            # while offline_recognizer.GetPendingChunks() != 0:
                            #     if offline_recognizer.GetPendingChunks() > 100:
                            #         slipping_time = 10
                            #     elif offline_recognizer.GetPendingChunks() > 50:
                            #         slipping_time = 5
                            #     elif offline_recognizer.GetPendingChunks() > 10:
                            #         slipping_time = 1
                            #     else:
                            #         slipping_time = 0.1
                            #     logging.debug(
                            #         f"В работе {offline_recognizer.GetPendingChunks()} частей. Пауза {slipping_time} сек.")
                            #     time.sleep(slipping_time)

                            #  Todo  добавить в Sate количество времени.
                            # Попытка построчного вывода

                            results = []

                            results.append(offline_recognizer.FinalResult())

                            #  Вычисляем скорость речи пользователя
                            for res in results:
                                jres = ujson.loads(res)
                                if not "result" in jres:
                                    continue
                                words = jres["result"]

                            between_words_delta = []
                            end_time = words[0].get('end')

                            for word in words[1::]:
                                between_words_delta.append(word.get('end') - end_time)
                                end_time = word.get('end')

                        except Exception as e:
                            logging.error(f'Ошибка при передаче на распознавание {file_path}: {e}')
                        else:
                            logging.debug("Распознали")
                            logging.debug(
                                f"Обработали аудио канал № {channel + 1} за {datetime.now() - time_rec_start} сек.")

                            # Собрали прям все ответы.
                            raw_recognition.append(results)

            # Добавляем пунктуацию
            # cased = subprocess.check_output('python3 recasepunc/recasepunc.py predict recasepunc/checkpoint',
            #                                 shell=True, text=True, input=recognized_text)
            #
            # logging.debug(f"Результат распознавания текста - {cased}")

        if not is_async:
            logging.debug(f'Передал результат работы функции в response')
            result = {
                "error": error,
                "error_description": error_description,
                "data"
                "duration": sound_duration,
                "raw_recognition": raw_recognition
                    }
            return result

        else:
            logging.debug(State.request_data)
            State.response_data[task_id]['error'] = error
            State.response_data[task_id]['state'] = 'error_description'  # Todo перевести в еррор и описание
            State.response_data[task_id]['duration'] = sound_duration
            State.response_data[task_id]['raw_recognition'] = raw_recognition


if __name__ == '__main__':
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    # file = Path("Classifier/content/2723.mp3").is_file()
    print('Требуется норм запуск')
    data = offline_recognition('')

"https://proglib.io/p/reshaem-zadachu-perevoda-russkoy-rechi-v-tekst-s-pomoshchyu-python-i-biblioteki-vosk-2022-06-30"
"https://stackoverflow.com/questions/29547218/remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub"
"https://habr.com/ru/articles/735480/"
