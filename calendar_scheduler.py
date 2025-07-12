import sched, time, datetime
import calendar
from enum import Enum
import threading

SECONDS_IN_DAY = 86400
SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60


# TODO: учесть часовой пояс, так как time.time() возвращает время в UTC


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
        if 1 > interval:
            return None
        event = Event(self._scheduler)
        if start_time is None:
            start_time = self.timefunc()
        interval_ms = interval / 1000
        self._enter_every_millisecond_event(event, start_time, interval_ms, end_time, action, args, kwargs)
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
        if 1 > interval:
            return None
        event = Event(self._scheduler)

        if start_time is None:
            start_time = self.timefunc()

        self._enter_every_second_event(event, start_time, interval, end_time, action, args, kwargs)
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
        action, action_args=(), action_kwargs=_sentinel,
        interval: int = 1,
        hour: int = 0, minute: int = 0, second: int = 0,
        start_time: float = None, end_time: float = None
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

    def enter_weekly_event(
        self,
        action, action_args=(), action_kwargs=_sentinel,
        interval: int = 1,
        day: calendar.Day = calendar.Day.MONDAY, hour: int = 0, minute: int = 0, second: int = 0,
        start_time: float = None, end_time: float = None
    ):
        if (1 > interval) or (0 > hour > 23) or (0 > minute > 59) or (0 > second > 59):
            return None

        event = Event(self._scheduler)

        if start_time is None:
            start_time = self.timefunc()

        # Отматываем на секунду назад, чтобы первый запуск был в start_time.
        start_time -= 1

        self._enter_weekly_event(event, start_time, 604800*interval, day, hour, minute, second, end_time, action, action_args, action_kwargs)
        self._push()
        return event

    def _enter_every_millisecond_event(self, event: Event, start_time, interval, end_time, action, args, kwargs):
        def _next_time(base_time):
            return base_time + interval

        next_time = _next_time(start_time)

        current_time = self.timefunc()
        if current_time > next_time:
            next_time = _next_time(current_time)

        if end_time is not None and next_time >= end_time:
            return
    
        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_every_millisecond_event, event, (next_time,interval,end_time), action, args, kwargs)
        )

    def _enter_every_second_event(self, event: Event, start_time, interval, end_time, action, args, kwargs):
        def _next_time(base_time):
            return base_time + interval

        next_time = _next_time(start_time)

        current_time = self.timefunc()
        if current_time > next_time:
            next_time = _next_time(current_time)

        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_every_second_event, event, (next_time,interval,end_time), action, args, kwargs)
        )

    def _enter_every_minute_event(self, event: Event, start_time, interval, second, end_time, action, action_args, action_kwargs):
        def _next_time(base_time):
            minute_start = base_time // SECONDS_IN_MINUTE * SECONDS_IN_MINUTE
            target_time = minute_start + second
            if target_time <= base_time:
                target_time += interval
            return target_time

        next_time = _next_time(start_time)
        current_time = self.timefunc()
        if current_time > next_time:
            next_time = _next_time(current_time)
        if end_time is not None and next_time >= end_time:
            return
        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_every_minute_event, event, (next_time,interval,second,end_time), action, action_args, action_kwargs)
        )

    def _enter_hourly_event(self, event: Event, start_time, interval, minute, second, end_time, action, action_args, action_kwargs):
        def _next_time(base_time):
            hour_start = base_time // SECONDS_IN_HOUR * SECONDS_IN_HOUR
            target_time = hour_start + minute * SECONDS_IN_MINUTE + second
            if target_time <= base_time:
                target_time += interval
            return target_time

        next_time = _next_time(start_time)
        current_time = self.timefunc()
        if current_time > next_time:
            next_time = _next_time(current_time)
        if end_time is not None and next_time >= end_time:
            return
        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_hourly_event, event, (next_time, interval, minute, second, end_time), action, action_args, action_kwargs)
        )

    def _enter_daily_event(self, event: Event, start_time, interval, hour, minute, second, end_time, action, action_args, action_kwargs):
        def _next_time(base_time):
            day_start = base_time // SECONDS_IN_DAY * SECONDS_IN_DAY
            target_time = day_start + hour * SECONDS_IN_HOUR + minute * SECONDS_IN_MINUTE + second
            if target_time <= base_time:
                target_time += interval
            return target_time

        next_time = _next_time(start_time)
        
        current_time = self.timefunc()
        if current_time > next_time:
            next_time = _next_time(current_time)

        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_daily_event, event, (next_time, interval, hour, minute, second, end_time), action, action_args, action_kwargs)
        )

    def _enter_weekly_event(self, event: Event, start_time, interval, day: calendar.Day, hour, minute, second, end_time, action, action_args, action_kwargs):
        def _next_time(base_time):
            start_day = int(base_time // SECONDS_IN_DAY)
            weekday = (start_day + 3) % 7
            days_ahead = (day.value - weekday) % 7
            midnight = (start_day + days_ahead) * SECONDS_IN_DAY
            target_time = midnight + hour * SECONDS_IN_HOUR + minute * SECONDS_IN_MINUTE + second
            if target_time <= base_time:
                target_time += interval
            return target_time

        next_time = _next_time(start_time)

        current_time = self.timefunc()
        if current_time > next_time:
            next_time = _next_time(current_time)
            
        if end_time is not None and next_time >= end_time:
            return

        event.internal_event = self._scheduler.enterabs(next_time, 0,
            action=self._action_runner,
            argument=(self._enter_weekly_event, event, (next_time, interval, day, hour, minute, second, end_time), action, action_args, action_kwargs)
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


    def enter_monthly_event(self, interval=1, day=0, hour=0, minute=0, second=0):
        # Если day больше, чем количество дней в месяце, то используется последний день месяца.
        # Если day=31 - для февраля day=28 или day = 29
        # Или лучше бросить исключение?
        raise NotImplementedError()
