"""
Calendar Scheduler core module.
This module provides the core functionality for scheduling recurring events.
"""

import sched
import time
import datetime
import calendar
from dataclasses import dataclass
import threading
from typing import Optional, Any


SECONDS_IN_MINUTE = 60

@dataclass()
class Event:
    """
    Represents a scheduled event in the calendar scheduler.
    Contains synchronization primitives and internal state for event management.
    Can be used to cancel the event using the CalendarScheduler.cancel() method.
    """
    lock: threading.Lock = threading.Lock()
    internal_event: Optional[sched.Event] = None
    canceled: bool = False


@dataclass(frozen=True)
class EventSettings:
    event: Event
    action: Any
    action_args: Any # tuple
    action_kwargs: Any # dict
    start_time: float
    end_time: Optional[float]
    tz: Optional[datetime.tzinfo] = None
    interval: int = 1
    second: int = 0
    minute: int = 0
    hour: int = 0
    weekday: int = 0
    day: int = 1
    month: int = 1


@dataclass(frozen=True)
class InternalEveryMillisecondEvent(EventSettings):
    interval_ms: float = None

    def next_time(self, run_time):
        return run_time + self.interval_ms


@dataclass(frozen=True)
class InternalEverySecondEvent(EventSettings):
    def next_time(self, run_time):
        target_time = run_time // 1 # remove milliseconds
        past_event = False
        if self.event.internal_event is not None:
            if target_time <= run_time:
                past_event = True
        elif target_time < run_time:
            past_event = True
        if past_event:
            target_time += self.interval
        return target_time


@dataclass(frozen=True)
class InternalEveryMinuteEvent(EventSettings):
    def next_time(self, run_time):
        minute_start = run_time // SECONDS_IN_MINUTE * SECONDS_IN_MINUTE
        target_time = minute_start + self.second
        past_event = False
        if self.event.internal_event is not None:
            if target_time <= run_time:
                past_event = True
        elif target_time < run_time:
            past_event = True
        if past_event:
            target_time += self.interval
        return target_time


@dataclass(frozen=True)
class InternalHourlyEvent(EventSettings):
    def next_time(self, run_time):
        dt_base_time = datetime.datetime.fromtimestamp(run_time, self.tz)
        target_time = dt_base_time.replace(minute=self.minute, second=self.second, microsecond=0)
        past_event = False
        if self.event.internal_event is not None:
            if target_time <= dt_base_time:
                past_event = True
        elif target_time < dt_base_time:
            past_event = True
        if past_event:
            target_time += datetime.timedelta(hours=self.interval)
        return target_time.timestamp()


@dataclass(frozen=True)
class InternalDailyEvent(EventSettings):
    def next_time(self, run_time):
        dt_base_time = datetime.datetime.fromtimestamp(run_time, self.tz)
        target_time = dt_base_time.replace(
            hour=self.hour, minute=self.minute, second=self.second, microsecond=0
        )

        past_event = False
        if self.event.internal_event is not None:
            if target_time <= dt_base_time:
                past_event = True
        elif target_time < dt_base_time:
            past_event = True
        if past_event:
            target_time += datetime.timedelta(days=self.interval)
        return target_time.timestamp()


@dataclass(frozen=True)
class InternalWeeklyEvent(EventSettings):
    def next_time(self, run_time):
        dt_base_time = datetime.datetime.fromtimestamp(run_time, self.tz)
        days_ahead = (self.weekday - dt_base_time.weekday()) % 7
        target_date = dt_base_time + datetime.timedelta(days=days_ahead)
        target_time = target_date.replace(
            hour=self.hour, minute=self.minute, second=self.second, microsecond=0
        )

        past_event = False
        if self.event.internal_event is not None:
            if target_time <= dt_base_time:
                past_event = True
        elif target_time < dt_base_time:
            past_event = True
        if past_event:
            target_time += datetime.timedelta(weeks=self.interval)
        return target_time.timestamp()


@dataclass(frozen=True)
class InternalMonthlyEvent(EventSettings):
    def next_time(self, run_time):
        dt_base_time = datetime.datetime.fromtimestamp(run_time, self.tz)
        last_day = calendar.monthrange(dt_base_time.year, dt_base_time.month)[1]
        limit_day = min(self.day, last_day)
        target_time = dt_base_time.replace(
            day=limit_day, hour=self.hour, minute=self.minute, second=self.second, microsecond=0
        )
        past_event = False
        if self.event.internal_event is not None:
            if target_time <= dt_base_time:
                past_event = True
        elif target_time < dt_base_time:
            past_event = True
        if past_event:
            next_month = dt_base_time.month + self.interval
            next_year = dt_base_time.year + (next_month - 1) // 12
            next_month = (next_month - 1) % 12 + 1
            last_day = calendar.monthrange(next_year, next_month)[1]
            limit_day = min(self.day, last_day)
            target_time = datetime.datetime(
                next_year, next_month, limit_day, self.hour, self.minute, self.second,
                tzinfo=self.tz
            )
        return target_time.timestamp()


@dataclass(frozen=True)
class InternalYearlyEvent(EventSettings):
    def next_time(self, run_time):
        dt_base_time = datetime.datetime.fromtimestamp(run_time, self.tz)
        last_day = calendar.monthrange(dt_base_time.year, self.month)[1]
        limit_day = min(self.day, last_day)
        target_time = dt_base_time.replace(
            month=self.month, day=limit_day, hour=self.hour,
            minute=self.minute, second=self.second, microsecond=0
        )
        past_event = False
        if self.event.internal_event is not None:
            if target_time <= dt_base_time:
                past_event = True
        elif target_time < dt_base_time:
            past_event = True
        if past_event:
            next_year = dt_base_time.year + self.interval
            last_day = calendar.monthrange(next_year, self.month)[1]
            limit_day = min(self.day, last_day)
            target_time = datetime.datetime(
                next_year, self.month, limit_day, self.hour, self. minute, self.second,
                tzinfo=self.tz
            )
        return target_time.timestamp()


_sentinel = object()


def _action_runner(enter_func, event_settings, cal_scheduler, event_time):
    if event_settings.action_kwargs is _sentinel:
        action_kwargs = {}
    else:
        action_kwargs = event_settings.action_kwargs
    with event_settings.event.lock:
        if event_settings.event.canceled:
            return
        enter_func(event_settings, cal_scheduler, event_time)
    event_settings.action(*event_settings.action_args, **action_kwargs)


class DefaultSleepController:
    def __init__(self):
        self._terminate_sleep = threading.Event()  # Используется, чтобы прерывать функцию sleep.

    def sleep(self, seconds):
        """
        Sleep for the specified number of seconds.

        :param seconds: Number of seconds to sleep.
        """
        self._terminate_sleep.clear()
        self._terminate_sleep.wait(seconds)

    def interrupt(self):
        """
        Interrupt the sleep.
        """
        self._terminate_sleep.set()


class CalendarScheduler:
    """
    Calendar scheduler.
    """
    def __init__(self, timefunc = time.time, sleep_controller=DefaultSleepController()):
        """
        Initialize the CalendarScheduler.

        :param timefunc: Function to get the current time (default: time.time).
        :param sleep_controller: Object handling sleep and interrupt logic
                                 (default: DefaultSleepController).
        """
        self.timefunc = timefunc
        self.sleep_controller = sleep_controller
        self._scheduler = sched.scheduler(timefunc, self.sleep_controller.sleep)

    def run(self):
        """
        Start the scheduler and run all scheduled events until completion.
        Completion means that all events have either been canceled or have reached their end_time.
        This method blocks the calling thread until all scheduled events have been processed.
        """
        self._scheduler.run()

    def cancel(self, event: Event):
        """
        Cancel a scheduled event.

        :param event: The event instance returned by the enter_*() method.
        """
        cancelled = False
        with event.lock:
            if event.canceled:
                return
            event.canceled = True
            if event.internal_event:
                try:
                    self._scheduler.cancel(event.internal_event)
                    cancelled = True
                except ValueError:
                    pass
            event.internal_event = None
        if cancelled:
            self._push()

    def _sleep(self, seconds):
        self.sleep_controller.sleep(seconds)

    def _push(self):
        self.sleep_controller.interrupt()

    def _enter_event(self, event_settings, timefunc, run_time):
        next_time = event_settings.next_time(run_time)

        current_time = timefunc()
        if current_time > next_time:
            next_time = event_settings.next_time(current_time)

        if event_settings.end_time is not None and next_time >= event_settings.end_time:
            return

        event_settings.event.internal_event = self._scheduler.enterabs(
            time=next_time,
            priority=0,
            action=_action_runner,
            argument=(self._enter_event, event_settings, timefunc, next_time)
        )

    def enter_every_millisecond_event(
            self,
            action,
            action_args=(),
            action_kwargs=_sentinel,
            interval: int = 100,
            start_time: float = None,
            end_time: float = None
    ):
        """
        Schedule an event to run every N milliseconds.

        :param action: The function to execute, when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in milliseconds (default: 100).
                         Very small intervals do not make practical sense.
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if 1 > interval:
            return None

        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        second_event = InternalEveryMillisecondEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, interval_ms=interval/1000
        )

        self._enter_event(second_event, self.timefunc, start_time)

        self._push()
        return event

    def enter_every_second_event(
            self,
            action,
            action_args=(),
            action_kwargs=_sentinel,
            interval: int = 1,
            start_time: float = None,
            end_time: float = None
    ):
        """
        Schedule an event to run every N seconds.

        :param action: The function to execute, when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in seconds (default: 1).
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if 1 > interval:
            return None
        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        second_event = InternalEverySecondEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, interval=interval
        )

        self._enter_event(second_event, self.timefunc, start_time)

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
        """
        Schedule an event to run every N minutes at a specific second.

        :param action: The function to execute, when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in minutes (default: 1).
        :param second: Second of the minute to run the event (default: 0). Range: 0-59.
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if (1 > interval) or not (0 <= second <= 59):
            return None

        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        minute_event = InternalEveryMinuteEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, interval=SECONDS_IN_MINUTE*interval, second=second
        )

        self._enter_event(minute_event, self.timefunc, start_time)

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
        end_time: float = None,
        tz: datetime.tzinfo = None
    ):
        """
        Schedule an event to run hourly (or every N hours) at a specific minute and second.

        :param action: The function to execute when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in hours (default: 1).
        :param minute: Minute of the hour to run the event (default: 0). Range: 0-59.
        :param second: Second of the minute to run the event (default: 0). Range: 0-59.
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :param tz: Time zone information for the event. None means local time.
                   Otherwise, should be an instance of tzinfo. For UTC, use datetime.timezone.utc.
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if (1 > interval) or not (0 <= minute <= 59) or not (0 <= second <= 59):
            return None

        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        hourly_event = InternalHourlyEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, tz, interval, second, minute
        )

        self._enter_event(hourly_event, self.timefunc, start_time)

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
        end_time: float = None,
        tz: datetime.tzinfo = None
    ):
        """
        Schedule an event to run daily (or every N days) at a specific time.

        :param action: The function to execute, when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in days (default: 1).
        :param hour: Hour of the day to run the event (default: 0). Range: 0-23.
        :param minute: Minute of the hour to run the event (default: 0). Range: 0-59.
        :param second: Second of the minute to run the event (default: 0). Range: 0-59.
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :param tz: Time zone information for the event. None means local time.
                   Otherwise, should be an instance of tzinfo. For UTC, use datetime.timezone.utc.
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if (
            (1 > interval) or not (0 <= hour <= 23) or not (0 <= minute <= 59)
            or not (0 <= second <= 59)
        ):
            return None

        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        daily_event = InternalDailyEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, tz, interval, second, minute, hour
        )

        self._enter_event(daily_event, self.timefunc, start_time)

        self._push()
        return event

    def enter_weekly_event(
        self,
        action,
        action_args=(),
        action_kwargs=_sentinel,
        interval: int = 1,
        weekday: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        start_time: float = None,
        end_time: float = None,
        tz: datetime.tzinfo = None
    ):
        """
        Schedule an event to run weekly (or every N weeks) on a specific day and time.

        :param action: The function to execute when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in weeks (default: 1).
        :param weekday: Day of the week as an integer, where Monday is 0, and Sunday is 6
                        Default: 0 (Monday).
        :param hour: Hour of the day to run the event (default: 0). Range: 0-23.
        :param minute: Minute of the hour to run the event (default: 0). Range: 0-59.
        :param second: Second of the minute to run the event (default: 0). Range: 0-59.
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :param tz: Time zone information for the event. None means local time.
                   Otherwise, should be an instance of tzinfo. For UTC, use datetime.timezone.utc.
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if (
            (1 > interval) or not (0 <= hour <= 23) or not (0 <= minute <= 59)
            or not (0 <= second <= 59) or not (0 <= weekday <= 6)
        ):
            return None

        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        daily_event = InternalWeeklyEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, tz, interval, second, minute, hour, weekday=weekday
        )

        self._enter_event(daily_event, self.timefunc, start_time)

        self._push()
        return event

    def enter_monthly_event(
        self,
        action,
        action_args=(),
        action_kwargs=_sentinel,
        interval: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        start_time: float = None,
        end_time: float = None,
        tz: datetime.tzinfo = None
    ):
        """
        Schedule an event to run monthly (or every N months) on a specific day and time.

        :param action: The function to execute, when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in months (default: 1).
        :param day: Day of the month to run the event (default: 1). Should be in range 1-31.
        :param hour: Hour of the day to run the event (default: 0). Should be in range 0-23.
        :param minute: Minute of the hour to run the event (default: 0). Should be in range 0-59.
        :param second: Second of the minute to run the event (default: 0). Should be in range 0-59.
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :param tz: Time zone information for the event. None means local time.
                   Otherwise, should be an instance of tzinfo. For UTC, use datetime.timezone.utc.
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if (
            (interval < 1) or not (1 <= day <= 31) or not (0 <= hour <= 23)
            or not (0 <= minute <= 59) or not (0 <= second <= 59)
        ):
            return None

        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        monthly_event = InternalMonthlyEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, tz, interval, second, minute, hour, day=day
        )

        self._enter_event(monthly_event, self.timefunc, start_time)

        self._push()
        return event

    def enter_yearly_event(
        self,
        action,
        action_args=(),
        action_kwargs=_sentinel,
        interval: int = 1,
        month: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        start_time: float = None,
        end_time: float = None,
        tz: datetime.tzinfo = None
    ):
        """
        Schedule an event to run yearly (or every N years) on a specific month, day, and time.

        :param action: The function to execute, when the event is triggered.
        :param action_args: Positional arguments for the action.
        :param action_kwargs: Keyword arguments for the action.
        :param interval: Interval in years (default: 1).
        :param month: Month to run the event (default: 1). Should be in the range 1-12.
        :param day: Day of the month to run the event (default: 1). Should be in the range 1-31.
        :param hour: Hour of the day to run the event (default: 0). Should be in the range 0-23.
        :param minute: Minute of the hour to run the event (default: 0).
                       Should be in the range 0-59.
        :param second: Second of the minute to run the event (default: 0).
                       Should be in the range 0-59.
        :param start_time: Start time for the event as a POSIX timestamp (default: now).
                           Should be the value returned by time.time() or datetime.timestamp().
        :param end_time: End time for the event as a POSIX timestamp (default: no limit).
                         Should be the value returned by time.time() or datetime.timestamp().
        :param tz: Time zone information for the event. None means local time.
                   Otherwise, should be an instance of tzinfo. For UTC, use datetime.timezone.utc.
        :return: The scheduled event object, or None if parameters are invalid.
        """
        if (
            (interval < 1) or not (1 <= month <= 12) or not (1 <= day <= 31)
            or not (0 <= hour <= 23) or not (0 <= minute <= 59) or not (0 <= second <= 59)
        ):
            return None

        event = Event()

        if start_time is None:
            start_time = self.timefunc()

        if end_time is not None and start_time >= end_time:
            return None

        yearly_event = InternalYearlyEvent(
            event, action, action_args, action_kwargs,
            start_time, end_time, tz, interval, second, minute, hour, day=day, month=month
        )

        self._enter_event(yearly_event, self.timefunc, start_time)

        self._push()
        return event
