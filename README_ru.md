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

```python
import datetime
from calsched import CalendarScheduler

def print_time():
    print(datetime.datetime.now())

scheduler = CalendarScheduler()
scheduler.enter_every_second_event(action=print_time)
scheduler.run()
```

В этом случае run() заблокирует поток, в котором он запущен.

Функция, передаваемая в action выполняется в том же потоке, что и метод run().

Если хочется добавлять события после запуска, то нужно добавить пустое событие перед вызовом run(), чтобы заставить планировщик работать.

    scheduler = CalendarScheduler()
    stub_event = scheduler.enter_hourly_event(action=lambda:None)
    scheduler.run()

Остановить run() можно отменив событие:

    scheduler.cancel(stub_event)

Если событий несколько, то для остановки планировщика нужно отменить все события.

Пример запуска в отдельном потоке:

```python
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
```

## Добавление событий

Для добавления событий используются методы `enter_*_event()`:

- `enter_every_millisecond_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N миллисекунд.
- `enter_every_second_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N секунд.
- `enter_every_minute_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N минут.
- `enter_hourly_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N часов.
- `enter_daily_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N дней.
- `enter_weekly_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N недель.
- `enter_monthly_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N месяцев.
- `enter_yearly_event(action=my_action, interval=N)` – my_action() будет запускаться с периодом N лет.

Параметр interval должен быть больше или равен 1 и сверху ничем не ограничен.

По умолчанию интервал равен 1. То есть, если не указать параметр interval, то событие будет запускаться с периодом 1 секунда, 1 минута и так далее в зависимости от метода. Кроме метода `enter_every_millisecond_event()`, где по умолчанию интервал равен 100 миллисекунд, поскольку интервал в 1 миллисекунду не возможно выдержать на реальных машинах.

Пример ежедневного события, которое выводит текущее время:

```python
import datetime
from calsched import CalendarScheduler
    
def print_time():
    print(datetime.datetime.now())

scheduler = CalendarScheduler()
scheduler.enter_daily_event(action=print_time)
scheduler.run()
```

### Параметры времени

Событие может выполняться в заданный момент времени, в конкретную секунду, минуту, час, день и/или месяц.

Метод enter_yearly_event() позволяет задать месяц, день, час, минуту и секунду. Пример события, которое выполняется за 5 минут до нового года (то есть 31 декабря в 23:55:00):

    scheduler.enter_yearly_event(action=my_action, month=12, day=31, hour=23, minute=55, second=0)

Для ежемесячных событий можно задать день, час, минуту и секунду. Пример события, которое выполняется в первый день каждого месяца в 04:00:00:

    scheduler.enter_monthly_event(action=my_action, day=1, hour=4, minute=0, second=0)

Для ежемесячных событий нельзя задать month, поскольку это не имеет смысла. Аналогично для остальных типов событий:

    scheduler.enter_weekly_event(action=my_action, day=calendar.Day.THURSDAY, hour=4, minute=0, second=0)
    scheduler.enter_daily_event(action=my_action, hour=4, minute=0, second=0)
    scheduler.enter_hourly_event(action=my_action, minute=0, second=0)
    scheduler.enter_every_minute_event(action=my_action, second=0)

У `методов enter_every_second_event` и `enter_every_millisecond_event` нет возможности указать время исполнения.

Значения параметров времени должны быть в диапазоне:

- 0 <= `second` <= 59,
- 0 <= `minute` <= 59,
- 0 <= `hour` <= 23,
- 1 <= `day` <= 31,
- 0 <= `weekday` <= 6 (0 – понедельник, 6 – воскресенье),
- 1 <= `month` <= 12.

В методах `enter_monthly_event()` и `enter_yearly_event()` если указан день больше, чем количество дней в месяце, то событие будет выполняться в последний день месяца. Например, если указать `day=31`, то событие выполнится 31 января, затем 28 февраля или 29 февраля (в високосный год).

### Начало и конец периодического события

Можно задать время начала и конца периодического события. Для этого используются параметры `start_time` и `end_time`. Если не задать эти параметры, то событие будет выполняться бесконечно начиная с текущего момента времени.

`start_time` – время первого выполнения.
`end_time` – время, до которого будет выполняться событие.

Параметры `start_time` и `end_time` задаются в формате timestamp (количество секунд с начала эпохи Unix, то есть с 1 января 1970 года). Обычно такие значения получают с помощью функций time.time() или datetime.timestamp().

То есть диапазон времени от `start_time` до `end_time` (не включительно).

Все методы `enter_*_event()` позволяют задать `start_time` и `end_time`. Пример события, которое выполняется каждый день с 1 января 2024 года по 1 января 2025 года (не включительно):

    start_time = datetime.datetime(2024, 1, 1, 0, 0, 0).timestamp()
    end_time = datetime.datetime(2025, 1, 1, 0, 0, 0).timestamp()
    scheduler.enter_daily_event(action=my_action, start_time=start_time, end_time=end_time)

### Аргументы функции действия

Функция действия может принимать аргументы. Для этого нужно использовать параметры `action_args` для позиционных аргументов и `action_kwargs` для именованных аргументов.

Все методы `enter_*_event()` позволяют задать `action_args` и `action_kwargs`.

Пример:

```python
def my_action(arg1, arg2):
    pass

scheduler.enter_daily_event(action=my_action, action_args=("Hello",), action_kwargs={"arg2": 123})
```

Планировщик вызовет функцию `my_action()` следующим образом:

    my_action("Hello", arg2=123)
