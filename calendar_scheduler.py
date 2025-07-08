"""

Алгоритм

Добавление задачи:
1. Останавливаем планировщик.
2. Добавляем задачу.
3. Запускаем планировщик.

Выполнение задачи:
1. Вызывается промежуточный коллбек.
2. Формируем очередную задачу и кладем в очередь.
3. Запускаем оригинальный коллбек.

Остановка планировщика:

1. Отменяются все задачи.
2. Дожидаемся выполнения последней задачи.
3. Завершаем run().

Отмена задач:

1. Отменяем все задачи.
2. Функция run() не завершается, а ждет появления новых задач.

"""


import sched, time, datetime
from enum import Enum
import threading


class Event:
    def __init__(self, scheduler):
        self.lock = threading.Lock()
        self._scheduler = scheduler
        self.internal_event = None
        self.canceled = False

    def cancel(self):
        """
        Cancel an event.

        This must be presented the ID as returned by enter().
        If the event is not in the queue, this raises ValueError.

        Вызов cancel() не влияет на уже запущенную функцию action().
        """
        with self.lock:
            if self.canceled:
                return
            self.canceled = True
            if self.internal_event:
                try:
                    self._scheduler.cancel(self.internal_event)
                except ValueError:
                    pass
            self.internal_event = None


# TODO: использовать готовый модуль calendar
class Week(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

_sentinel = object()


class DefaultSleepController:
    def __init__(self):
        self._terminate_sleep = threading.Event()  # Используется, чтобы прерывать функцию sleep.

    def sleep(self, seconds):
        self._terminate_sleep.wait(seconds)
        self._terminate_sleep.clear()

    def interrupt(self):
        self._terminate_sleep.set()


class CalendarScheduler:
    def __init__(self, timefunc = time.time, sleep_controller=DefaultSleepController()):
        self.timefunc = timefunc
        self.sleep_controller = sleep_controller
        self._terminate_sleep = threading.Event() # Используется, чтобы прерывать функцию sleep.
        self._stopped = False
        self._run = threading.Event()
        self._scheduler = sched.scheduler(timefunc, self.sleep_controller.sleep)

    def run(self):
        if self._stopped:
            return
        self._scheduler.run()

    def run_forever(self):
        # Если есть задачи, у которых просрочено время, то они выполнятся сразу после запуска.
        # Функция завершится после отмены всех задач с помощью функции cancel(),
        # и после завершения выполняющейся задачи.
        # Для завершения метода run(), нужно вызвать метод stop().
        # После завершения, повторно запустить не получится.
        if self._stopped:
            return
        while True:
            self._run.wait()
            self._scheduler.run()
            self._run.clear()
            if self._stopped:
                break

    def no_more_events(self):
        """
        Stops the loop of waiting for events.
        If there are no more events, then the run_forever() function ends.
        """
        self._stopped = True
        self._run.set()

    def _sleep(self, seconds):
        self.sleep_controller.sleep(seconds)

    def _push(self):
        self.sleep_controller.interrupt()
        self._run.set()

    # Слишком малые интервалы не имеют практического смысла, так как перестают соблюдаться.
    def enter_every_millisecond_event(
            self,
            action,
            args=(),
            kwargs=_sentinel,
            interval: int = 100,
            start_time: float = None,
            end_time: float = None
    ):
        if 1 > interval > 999:
            return None
        event = Event(self._scheduler)
        if start_time is None:
            start_time = self.timefunc()
        interval_ms = interval / 1000
        self._enter_every_millisecond_event(event, interval_ms, start_time, end_time, action, args, kwargs)
        self._push()
        return event

    def enter_every_second_event(
            self,
            action,
            args=(),
            kwargs=_sentinel,
            interval: int = 1,
            start_time: float = None,
            end_time: float = None
    ):
        if 1 > interval > 59:
            return None
        event = Event(self._scheduler)
        self._enter_every_second_event(event, interval, start_time, end_time, action, args, kwargs)
        self._push()
        return event

    def enter_every_minute_event(
        self,
        action,
        action_args=(),
        action_kwargs=_sentinel,
        interval: int = 1,
        second: int = 0,
        start_time: float = None,
        end_time: float = None
    ):
        if (1 > interval) or (0 > second > 59):
            return None

        event = Event(self._scheduler)

        if start_time is None:
            start_time = self.timefunc()

        # Отматываем на секунду назад, чтобы первый запуск был в start_time.
        start_time -= 1

        self._enter_every_minute_event(event, start_time, 60*interval, second, end_time, action, action_args, action_kwargs)
        self._push()
        return event

    def enter_hourly_event(
        self,
        action,
        action_args=(),
        action_kwargs=_sentinel,
        interval: int = 1,
        minute: int = 0,
        second: int = 0,
        start_time: float = None,
        end_time: float = None
    ):
        if (1 > interval) or (0 > minute > 59) or (0 > second > 59):
            return None

        event = Event(self._scheduler)

        if start_time is None:
            start_time = self.timefunc()

        # Отматываем на секунду назад, чтобы первый запуск был в start_time.
        start_time -= 1

        self._enter_hourly_event(event, start_time, 3600*interval, minute, second, end_time, action, action_args, action_kwargs)
        self._push()
        return event

    def enter_daily_event(
        self,
        action,
        action_args=(),
        action_kwargs=_sentinel,
        interval: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        start_time: float = None,
        end_time: float = None
    ):
        if (1 > interval) or (0 > hour > 23) or (0 > minute > 59) or (0 > second > 59):
            return None

        event = Event(self._scheduler)

        if start_time is None:
            start_time = self.timefunc()

        # Отматываем на секунду назад, чтобы первый запуск был в start_time.
        start_time -= 1

        self._enter_daily_event(event, start_time, 86400*interval, hour, minute, second, end_time, action, action_args, action_kwargs)
        self._push()
        return event

    def _enter_every_millisecond_event(self, event: Event, interval, start_time, end_time, action, args, kwargs):
        if event.internal_event is not None:
            next_time = event.internal_event.time + interval
        else:
            # TODO: нужно посчитать только один раз при первом запуске.
            if start_time is None:
                start_time = self.timefunc()
                next_time = start_time + interval
            else:
                next_time = start_time

        current_time = self.timefunc()

        if current_time > next_time:
            next_time = current_time

        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_every_millisecond_event, event, (interval,start_time,end_time), action, args, kwargs)
        )

    def _enter_every_second_event(self, event: Event, interval, start_time, end_time, action, args, kwargs):
        if event.internal_event is not None:
            next_time = event.internal_event.time + interval
        else:
            # TODO: нужно посчитать только один раз при первом запуске.
            if start_time is None:
                start_time = self.timefunc()
                next_time = start_time + interval
            else:
                next_time = start_time

        current_time = self.timefunc()
        if current_time > next_time:
            next_time = current_time

        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_every_second_event, event, (interval,start_time,end_time), action, args, kwargs)
        )

    def _enter_every_minute_event(self, event: Event, start_time, interval, second, end_time, action, action_args, action_kwargs):
        start_minute = start_time // 60 * 60
        start_second = start_time % 60
        next_time = start_minute + second
        if start_second >= second:
            next_time += interval

        current_time = self.timefunc()
        if current_time > next_time:
            next_time = current_time

        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_every_minute_event, event, (next_time,interval,second,end_time), action, action_args, action_kwargs)
        )

    def _enter_hourly_event(self, event: Event, start_time, interval, minute, second, end_time, action, action_args, action_kwargs):
        start_hour = start_time // 3600 * 3600
        start_minute = start_time % 3600 // 60
        start_second = start_time % 60
        next_time = start_hour + 60 * minute + second

        if start_minute > minute or (start_minute == minute and start_second >= second):
            next_time += interval

        current_time = self.timefunc()
        if current_time > next_time:
            next_time = current_time

        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_hourly_event, event, (next_time, interval, minute, second, end_time), action, action_args, action_kwargs)
        )

    def _enter_daily_event(self, event: Event, start_time, interval, hour, minute, second, end_time, action, action_args, action_kwargs):
        start_day = start_time // 86400 * 86400
        start_hour = start_time % 86400 // 3600
        start_minute = start_time % 3600 // 60
        start_second = start_time % 60
        next_time = start_day + 3600 * hour + 60 * minute + second

        if (
               (start_hour > hour)
            or (start_hour == hour and start_minute > minute)
            or (start_hour == hour and start_minute == minute and start_second >= second)
        ):
            next_time += interval

        current_time = self.timefunc()
        if current_time > next_time:
            next_time = current_time

        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_daily_event, event, (next_time, interval, hour, minute, second, end_time), action, action_args, action_kwargs)
        )

    @staticmethod
    def _action_runner(enter_func, event, time_args, action, action_args, action_kwargs):
        if action_kwargs is _sentinel:
            action_kwargs = {}
        with event.lock:
            if event.canceled:
                return
            enter_func(event, *time_args, action, action_args, action_kwargs)
        action(*action_args, **action_kwargs)


    def enter_weekly_event(self, interval=1, day_of_week=Week.Monday, hour=0, minute=0, second=0):
        raise NotImplementedError()

    def enter_monthly_event(self, interval=1, day=0, hour=0, minute=0, second=0):
        # Если day больше, чем количество дней в месяце, то используется последний день месяца.
        # Если day=31 - для февраля day=28 или day = 29
        # Или лучше бросить исключение?
        raise NotImplementedError()
