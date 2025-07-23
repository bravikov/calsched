# Calendar Scheduler for Recurring Events

[![PyPI version](https://img.shields.io/pypi/v/calsched.svg)](https://pypi.org/project/calsched/)
[![Pylint](https://github.com/bravikov/calsched/actions/workflows/pylint.yml/badge.svg)](https://github.com/bravikov/calsched/actions/workflows/pylint.yml)
[![Unit tests](https://github.com/bravikov/calsched/actions/workflows/unittests.yml/badge.svg)](https://github.com/bravikov/calsched/actions/workflows/unittests.yml)

[![ru](https://img.shields.io/badge/lang-russian-blue.svg)](README_ru.md)

## Features

- Executes an action function on a schedule.
- Thread-safe: events can be added and canceled from different threads.
- Supports intervals from milliseconds to years.
- Uses the standard `sched` scheduler.
- Timezone support.
- Syntax similar to `datetime`.
- Events can be added at any time: before or after the scheduler starts, and from any thread.
- No additional packages required.

## Installation

Install via pip:

```bash
pip install calsched
```

Install via uv:

```bash
uv pip install calsched
```

## Import

```python
from calsched import CalendarScheduler
```

## Creating the Scheduler

```python
scheduler = CalendarScheduler()
```

## Running the Scheduler

Start the scheduler using the `run()` method:

```python
scheduler.run()
```

However, it will immediately exit if no events are scheduled. At least one event must be scheduled before starting.

Example that prints the current time every second:

```python
import datetime
from calsched import CalendarScheduler

def print_time():
    print(datetime.datetime.now())

scheduler = CalendarScheduler()
scheduler.enter_every_second_event(action=print_time)
scheduler.run()
```

In this case, `run()` blocks the thread in which it is called.

The `action` function is executed in the same thread as the `run()` method.

To allow adding events after the scheduler has started, you can add a placeholder event before calling `run()` to keep the scheduler active:

```python
scheduler = CalendarScheduler()
stub_event = scheduler.enter_hourly_event(action=lambda: None)
scheduler.run()
```

You can stop `run()` by canceling the placeholder event:

```python
scheduler.cancel(stub_event)
```

If there are multiple events, you need to cancel all events to stop the scheduler.

Example of running in a separate thread:

```python
import datetime
import threading
from time import sleep
from calsched import CalendarScheduler

def print_time():
    print(datetime.datetime.now())

scheduler = CalendarScheduler()
stub_event = scheduler.enter_hourly_event(action=lambda: None)
thread = threading.Thread(target=scheduler.run)
thread.start()
sleep(1.0)

event = scheduler.enter_every_second_event(action=print_time)
sleep(5.0)
scheduler.cancel(stub_event)
scheduler.cancel(event)
thread.join()
```

## Adding Events

To add events, use the `enter_*_event()` methods:

- `enter_every_millisecond_event(action=my_action, interval=N)` – `my_action()` will be called every N milliseconds.
- `enter_every_second_event(action=my_action, interval=N)` – `my_action()` will be called every N seconds.
- `enter_every_minute_event(action=my_action, interval=N)` – `my_action()` will be called every N minutes.
- `enter_hourly_event(action=my_action, interval=N)` – `my_action()` will be called every N hours.
- `enter_daily_event(action=my_action, interval=N)` – `my_action()` will be called every N days.
- `enter_weekly_event(action=my_action, interval=N)` – `my_action()` will be called every N weeks.
- `enter_monthly_event(action=my_action, interval=N)` – `my_action()` will be called every N months.
- `enter_yearly_event(action=my_action, interval=N)` – `my_action()` will be called every N years.

The `interval` parameter must be greater than or equal to 1 and has no upper limit.

By default, the interval is 1. That is, if you do not specify the `interval` parameter, the event will be triggered every 1 second, 1 minute, etc., depending on the method. The exception is `enter_every_millisecond_event()`, where the default interval is 100 milliseconds, since a 1-millisecond interval is not feasible on real machines.

Example of a daily event that prints the current time:

```python
import datetime
from calsched import CalendarScheduler
    
def print_time():
    print(datetime.datetime.now())

scheduler = CalendarScheduler()
scheduler.enter_daily_event(action=print_time)
scheduler.run()
```

### Time Parameters

An event can be scheduled for a specific moment: a particular second, minute, hour, day, and/or month.

The `enter_yearly_event()` method allows you to specify month, day, hour, minute, and second. Example: an event that runs 5 minutes before New Year (i.e., December 31 at 23:55:00):

    scheduler.enter_yearly_event(action=my_action, month=12, day=31, hour=23, minute=55, second=0)

For monthly events, you can specify day, hour, minute, and second. Example: an event that runs on the first day of each month at 04:00:00:

    scheduler.enter_monthly_event(action=my_action, day=1, hour=4, minute=0, second=0)

For monthly events, you cannot specify `month`, as it does not make sense. Similarly for other event types:

    scheduler.enter_weekly_event(action=my_action, day=calendar.Day.THURSDAY, hour=4, minute=0, second=0)
    scheduler.enter_daily_event(action=my_action, hour=4, minute=0, second=0)
    scheduler.enter_hourly_event(action=my_action, minute=0, second=0)
    scheduler.enter_every_minute_event(action=my_action, second=0)

The `enter_every_second_event` and `enter_every_millisecond_event` methods do not allow specifying execution time.

Time parameter value ranges:

- 0 <= `second` <= 59,
- 0 <= `minute` <= 59,
- 0 <= `hour` <= 23,
- 1 <= `day` <= 31 (for `enter_monthly_event()` and `enter_yearly_event()`),
- `day` can be a value from the `calendar.Day` enumeration (for `enter_weekly_event()`),
- 1 <= `month` <= 12.

In `enter_monthly_event()` and `enter_yearly_event()`, if the specified day is greater than the number of days in the month, the event will be executed on the last day of the month. For example, if you specify `day=31`, the event will run on January 31, then on February 28 or 29 (in a leap year).

### Start and End Time for Periodic Events

You can specify the start and end time for a periodic event using the `start_time` and `end_time` parameters. If not specified, the event will run indefinitely starting from the current time.

- `start_time` – time of the first execution.
- `end_time` – time until which the event will be executed.

The `start_time` and `end_time` parameters are specified as timestamps (seconds since the Unix epoch, i.e., January 1, 1970). Typically, these values are obtained using `time.time()` or `datetime.timestamp()`.

The time range is from `start_time` up to, but not including, `end_time`.

All `enter_*_event()` methods allow specifying `start_time` and `end_time`. Example: an event that runs every day from January 1, 2024, to January 1, 2025 (not inclusive):

    start_time = datetime.datetime(2024, 1, 1, 0, 0, 0).timestamp()
    end_time = datetime.datetime(2025, 1, 1, 0, 0, 0).timestamp()
    scheduler.enter_daily_event(action=my_action, start_time=start_time, end_time=end_time)

### Action Function Arguments

The action function can accept arguments. Use the `action_args` parameter for positional arguments and `action_kwargs` for keyword arguments.

All `enter_*_event()` methods allow specifying `action_args` and `action_kwargs`.

Example:

```python
def my_action(arg1, arg2, arg3):
    pass

scheduler.enter_daily_event(action=my_action, action_args=("Hello",), action_kwargs={"arg2": 123})
```

The scheduler will call the function as follows:

    my_action("Hello", arg2=123)
