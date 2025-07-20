# Календарный планировщик регулярных событий

## Особенности

- Вызывает функцию-действие по расписанию.
- Поддержка многопоточности. Добавлять и отменять события можно из разных потоков.
- Интервалы от миллисекунд до годов.
- Использует стандартный планировщик sched.
- Поддержка временных зон.
- Синтаксис похожий на datetime.
- Добавлять события можно в любое время: до запуска планировщика и после запуска. И из любого потока.
- Не требует установки дополнительных пакетов.

## Установка

Установка с помощью pip:

    pip install calsched

Установка с помощью uv:

    uv pip install calsched

## Импорт

    from calsched import CalendarScheduler

## Создание планировщика

    scheduler = CalendarScheduler()

## Запуск

Планировщик запускается методом run():

    scheduler.run()

Но в этом случае он сразу завершится, так как не запланировано ни одно событие. Перед запуском должно быть запланировано хотя бы одно событие.

Пример, который раз в секунду выводит текущее время:

    import datetime
    from calsched import CalendarScheduler
    
    def print_time():
        print(datetime.datetime.now())

    scheduler = CalendarScheduler()
    scheduler.enter_every_second_event(action=print_time)
    scheduler.run()

В этом случае run() заблокирует поток, в котором он запущен.

Функция, передаваемая в action выполняется в том же потоке, что и метод run().

Если хочется добавлять события после запуска, то нужно добавить пустое событие перед вызовом run(), чтобы заставить планировщик работать.

    scheduler = CalendarScheduler()
    stub_event = scheduler.enter_hourly_event(action=lambda:None)
    scheduler.run()

Остановить run() можно отменив событие:

    scheduler.cancel(stub_event)

Пример запуска в отдельном потоке:

    import datetime
    import threading
    from time import sleep
    from calsched import CalendarScheduler
    
    def print_time():
        print(datetime.datetime.now())

    scheduler = CalendarScheduler()
    stub_event = scheduler.enter_hourly_event(action=lambda:None)
    thread = threading.Thread(target=scheduler.run)
    thread.start()
    sleep(1.0)

    event = scheduler.enter_every_second_event(action=print_time)
    sleep(5.0)
    scheduler.cancel(stub_event)
    scheduler.cancel(event)
    thread.join()
