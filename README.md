# Calendar Scheduler for Recurring Events

[![PyPI version](https://img.shields.io/pypi/v/calsched.svg)](https://pypi.org/project/calsched/)

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