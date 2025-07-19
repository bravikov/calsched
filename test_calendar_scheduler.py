import datetime
import unittest
import time
import calendar

from calendar_scheduler import CalendarScheduler


class TestTimeController:
    def __init__(self):
        self.clock = 0.0

    def sleep(self, seconds):
        self.clock += seconds

    def interrupt(self):
        pass

    def get_clock(self):
        return self.clock


class TestEveryMillisecond(unittest.TestCase):
    def test_interval_default(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 0.2:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_every_millisecond_event(action=action)
        events.append(event)
        scheduler.run()

        self.assertEqual([0.1, 0.2], clocks)

    def test_interval_1ms(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 0.003:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_every_millisecond_event(action=action, interval=1)
        events.append(event)
        scheduler.run()

        self.assertEqual([0.001, 0.002, 0.003], clocks)


class TestEverySecond(unittest.TestCase):
    def test_interval_default(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 5.0:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_every_second_event(action=action)
        events.append(event)
        scheduler.run()

        self.assertEqual([0.0, 1.0, 2.0, 3.0, 4.0, 5.0], clocks)

    def test_interval_2s(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 5.0:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_every_second_event(action=action, interval=2)
        events.append(event)
        scheduler.run()

        self.assertEqual([0.0, 2.0, 4.0, 6.0], clocks)


class TestEverySecondFirstTime(unittest.TestCase):
    def setUp(self):
        self.time_controller = TestTimeController()
        self.scheduler = CalendarScheduler(timefunc=self.time_controller.get_clock, sleep_controller=self.time_controller)
        self.event = None
        self.clock = None

    def action(self):
        self.event.cancel()
        self.clock = self.time_controller.get_clock()

    def test_1(self):
        self.event = self.scheduler.enter_every_second_event(action=self.action, start_time=20)
        self.scheduler.run()
        self.assertEqual(20.0, self.clock)

    def test_2(self):
        self.event = self.scheduler.enter_every_second_event(action=self.action, start_time=20.1)
        self.scheduler.run()
        self.assertEqual(21.0, self.clock)

    def test_3(self):
        self.event = self.scheduler.enter_every_second_event(action=self.action, start_time=20.1, interval=2)
        self.scheduler.run()
        self.assertEqual(22.0, self.clock)

    def test_4(self):
        self.event = self.scheduler.enter_every_second_event(action=self.action, start_time=20.1, interval=3)
        self.scheduler.run()
        self.assertEqual(23.0, self.clock)


class TestEveryMinute(unittest.TestCase):
    def test_interval_default(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 300.0:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_every_minute_event(action=action)
        events.append(event)
        scheduler.run()

        self.assertEqual(clocks, [0.0, 60.0, 120.0, 180.0, 240.0, 300.0])


class TestEveryMinuteFirstTime(unittest.TestCase):
    def setUp(self):
        self.time_controller = TestTimeController()
        self.scheduler = CalendarScheduler(timefunc=self.time_controller.get_clock, sleep_controller=self.time_controller)
        self.event = None
        self.clock = None

    def action(self):
        self.event.cancel()
        self.clock = self.time_controller.get_clock()

    def test_1(self):
        self.event = self.scheduler.enter_every_minute_event(action=self.action, start_time=20, second=30)
        self.scheduler.run()
        self.assertEqual(30.0, self.clock)

    def test_2(self):
        self.event = self.scheduler.enter_every_minute_event(action=self.action, start_time=30, second=30)
        self.scheduler.run()
        self.assertEqual(30.0, self.clock)

    def test_3(self):
        self.event = self.scheduler.enter_every_minute_event(action=self.action, start_time=40, second=30)
        self.scheduler.run()
        self.assertEqual(90.0, self.clock)

    def test_4(self):
        self.event = self.scheduler.enter_every_minute_event(action=self.action, start_time=60)
        self.scheduler.run()
        self.assertEqual(60, self.clock)

    def test_5(self):
        self.event = self.scheduler.enter_every_minute_event(action=self.action, start_time=60, interval=2)
        self.scheduler.run()
        self.assertEqual(60, self.clock)


class TestHourly(unittest.TestCase):
    def test_interval_default(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 18000:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_hourly_event(action=action, tz=datetime.timezone.utc)
        events.append(event)
        scheduler.run()

        self.assertEqual([0.0, 3600.0, 7200.0, 10800.0, 14400.0, 18000.0], clocks)


class TestHourlyFirstTime(unittest.TestCase):
    def setUp(self):
        self.time_controller = TestTimeController()
        self.scheduler = CalendarScheduler(timefunc=self.time_controller.get_clock, sleep_controller=self.time_controller)
        self.event = None
        self.clock = None

    def action(self):
        self.event.cancel()
        self.clock = self.time_controller.get_clock()

    def test_1(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, tz=datetime.timezone.utc, start_time=59, minute=1, second=0)
        self.scheduler.run()
        self.assertEqual(60.0, self.clock)

    def test_2(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, tz=datetime.timezone.utc, start_time=65, minute=1, second=5)
        self.scheduler.run()
        self.assertEqual(65.0, self.clock)

    def test_3(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, tz=datetime.timezone.utc, start_time=65, minute=1, second=6)
        self.scheduler.run()
        self.assertEqual(66.0, self.clock)

    def test_4(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, tz=datetime.timezone.utc, start_time=65, minute=1, second=4)
        self.scheduler.run()
        self.assertEqual(3664.0, self.clock)

    def test_5(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, tz=datetime.timezone.utc, start_time=3600)
        self.scheduler.run()
        self.assertEqual(3600.0, self.clock)

    def test_6(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, tz=datetime.timezone.utc, start_time=3600, interval=2)
        self.scheduler.run()
        self.assertEqual(3600.0, self.clock)


class TestDaily(unittest.TestCase):
    def test_interval_default(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 432000.0:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_daily_event(action=action, tz=datetime.timezone.utc)
        events.append(event)
        scheduler.run()

        self.assertEqual([0.0, 86400.0, 172800.0, 259200.0, 345600.0, 432000.0], clocks)


class TestDailyFirstTime(unittest.TestCase):
    def setUp(self):
        self.time_controller = TestTimeController()
        self.scheduler = CalendarScheduler(timefunc=self.time_controller.get_clock, sleep_controller=self.time_controller)
        self.event = None
        self.clock = None

    def action(self):
        self.event.cancel()
        self.clock = self.time_controller.get_clock()

    def test_1(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=3600, hour=2, minute=1, second=1)
        self.scheduler.run()
        self.assertEqual(7261, self.clock)

    def test_2(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=3660, hour=1, minute=2, second=1)
        self.scheduler.run()
        self.assertEqual(3721, self.clock)

    def test_3(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=3661, hour=1, minute=1, second=2)
        self.scheduler.run()
        self.assertEqual(3662, self.clock)

    def test_4(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=3662, hour=1, minute=1, second=2)
        self.scheduler.run()
        self.assertEqual(3662, self.clock)

    def test_5(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=3662, hour=1, minute=1, second=1)
        self.scheduler.run()
        self.assertEqual(90061, self.clock)

    def test_6(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=3662, hour=1, minute=0, second=1)
        self.scheduler.run()
        self.assertEqual(90001, self.clock)

    def test_7(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=7200, hour=1, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(90000, self.clock)

    def test_8(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=86400)
        self.scheduler.run()
        self.assertEqual(86400, self.clock)

    def test_9(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, tz=datetime.timezone.utc, start_time=86400, interval=2)
        self.scheduler.run()
        self.assertEqual(86400, self.clock)


class TestWeekly(unittest.TestCase):
    def test_interval_default(self):
        time_controller = TestTimeController()

        events = []
        clocks = []

        def action():
            if time_controller.get_clock() >= 2160000.0:
                events[0].cancel()
            clocks.append(time_controller.get_clock())

        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        event = scheduler.enter_weekly_event(action=action, tz=datetime.timezone.utc)
        events.append(event)
        scheduler.run()

        self.assertEqual([345600.0, 950400.0, 1555200.0, 2160000.0], clocks)


class TestWeeklyFirstTime(unittest.TestCase):
    def setUp(self):
        self.time_controller = TestTimeController()
        self.scheduler = CalendarScheduler(timefunc=self.time_controller.get_clock, sleep_controller=self.time_controller)
        self.event = None
        self.clock = None

    def action(self):
        self.event.cancel()
        self.clock = self.time_controller.get_clock()

    def test_first_occurrence_on_same_day(self):
        # Четверг, 00:00:00, start_time = 0, day=THURSDAY
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc,start_time=0, day=calendar.Day.THURSDAY, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, 0.0)

    def test_first_occurrence_on_monday(self):
        # Четверг, 00:00:00, start_time = 0, day=MONDAY
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc,start_time=0, day=calendar.Day.MONDAY, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, 4*86400.0)  # До следующего понедельника

    def test_next_week(self):
        # Четверг, 00:00:01, day=THURSDAY, значит, следующее срабатывание через неделю
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc, start_time=1, day=calendar.Day.THURSDAY, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, 604800.0)  # 7*24*3600

    def test_other_weekday(self):
        # Четверг -> суббота
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc, start_time=0, day=calendar.Day.SATURDAY, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, 2*86400.0)

    def test_with_time(self):
        # Стартуем в пятницу, ищем понедельник 12:34:56
        friday = 1*86400
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc, start_time=friday, day=calendar.Day.MONDAY, hour=12, minute=34, second=56)
        self.scheduler.run()
        # Пятница -> понедельник = 3 дня, плюс время
        expected = friday + 3*86400 + 12*3600 + 34*60 + 56
        self.assertEqual(self.clock, expected)

    def test_interval_2_weeks(self):
        # Стартуем в пятницу, ищем пятницу, интервал 2 недели
        friday = 1*86400
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc, start_time=friday, day=calendar.Day.FRIDAY, hour=0, minute=0, second=0, interval=2)
        self.scheduler.run()
        self.assertEqual(self.clock, friday)
        # Следующее срабатывание будет через 2 недели

    def test_start_time_equal_action_time_interval_1(self):
        friday = 1*86400
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc, start_time=friday, day=calendar.Day.FRIDAY)
        self.scheduler.run()
        self.assertEqual(self.clock, friday)

    def test_start_time_equal_action_time_interval_2(self):
        friday = 1*86400
        self.event = self.scheduler.enter_weekly_event(action=self.action, tz=datetime.timezone.utc, start_time=friday, day=calendar.Day.FRIDAY, interval=2)
        self.scheduler.run()
        self.assertEqual(self.clock, friday)


class TestRealEveryMillisecond(unittest.TestCase):
    def test_interval_50ms(self):
        events = []
        count = 0
        clocks = []

        def action():
            nonlocal count
            count += 1
            if count >= 50:
                events[0].cancel()
            clocks.append(time.time())
            print(time.time())

        scheduler = CalendarScheduler()
        event = scheduler.enter_every_millisecond_event(action=action, interval=50)
        events.append(event)
        scheduler.run()

        for i in range(49):
            self.assertAlmostEqual(clocks[i+1] - clocks[i], 0.05, delta=0.01, msg=clocks)


class TestRealEverySecond(unittest.TestCase):
    def test_default_interval(self):
        events = []
        count = 0
        clocks = []

        def action():
            nonlocal count
            count += 1
            if count >= 5:
                events[0].cancel()
            clocks.append(time.time())

        scheduler = CalendarScheduler()
        event = scheduler.enter_every_second_event(action=action)
        events.append(event)
        scheduler.run()

        for i in range(4):
            self.assertAlmostEqual(clocks[i+1] - clocks[i], 1.0, delta=0.01, msg=clocks)


@unittest.skip("so long")
class TestRealEveryMinute(unittest.TestCase):
    def test_default_interval(self):
        events = []
        count = 0
        clocks = []

        def action():
            print(datetime.datetime.now())
            nonlocal count
            count += 1
            if count >= 5:
                events[0].cancel()
            clocks.append(time.time())

        scheduler = CalendarScheduler()
        event = scheduler.enter_every_minute_event(action=action)
        events.append(event)
        scheduler.run()

        for i in range(4):
            self.assertAlmostEqual(clocks[i+1] - clocks[i], 60.0, delta=0.1, msg=clocks)


class TestMonthlyFirstTime(unittest.TestCase):
    def setUp(self):
        self.time_controller = TestTimeController()
        self.scheduler = CalendarScheduler(timefunc=self.time_controller.get_clock, sleep_controller=self.time_controller)
        self.event = None
        self.clock = None

    def action(self):
        self.event.cancel()
        self.clock = self.time_controller.get_clock()

    def test_first_occurrence_before(self):
        start = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_monthly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, day=5, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())

    def test_first_occurrence_at(self):
        start = datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_monthly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, day=5, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())

    def test_first_occurrence_after(self):
        start = datetime.datetime(1970, 1, 6, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_monthly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, day=5, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1970, 2, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())

    def test_with_time(self):
        start = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_monthly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, day=5, hour=12, minute=34, second=56)
        self.scheduler.run()
        expected = datetime.datetime(1970, 1, 5, 12, 34, 56, tzinfo=datetime.timezone.utc).timestamp()
        self.assertEqual(self.clock, expected)

    def test_interval_2_months(self):
        start = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_monthly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, day=5, hour=0, minute=0, second=0, interval=2)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())


class TestMonthly(unittest.TestCase):
    def test_first_day_of_month(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 3:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_monthly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, day=1, hour=0, minute=0, second=0)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 2, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 3, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 4, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
        ])

    def test_last_day_of_month(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 2:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 31, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_monthly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, day=31, hour=0, minute=0, second=0)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 1, 31, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 2, 28, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 3, 31, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
        ])

    def test_february_leap(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 2:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1972, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_monthly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, day=29, hour=0, minute=0, second=0)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1972, 1, 29, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1972, 2, 29, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1972, 3, 29, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
        ])

    def test_interval_2_months(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 3:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_monthly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, interval=2, day=2, hour=0, minute=0, second=0)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 3, 2, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 5, 2, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 7, 2, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
        ])

    def test_with_time(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 2:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_monthly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, day=2, hour=1, minute=2, second=3)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 1, 2, 1, 2, 3, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 2, 2, 1, 2, 3, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1970, 3, 2, 1, 2, 3, tzinfo=datetime.timezone.utc).timestamp(),
        ])


class TestYearly(unittest.TestCase):
    def test_jan_5_every_year(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 4:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_yearly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, month=1, day=5, hour=0, minute=0, second=0)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1971, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1972, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1973, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1974, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
        ])

    def test_last_day_of_february(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 3:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_yearly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, month=2, day=29, hour=0, minute=0, second=0)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 2, 28, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1971, 2, 28, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1972, 2, 29, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1973, 2, 28, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
        ])

    def test_interval_3_years(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 3:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_yearly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, month=1, day=1, hour=0, minute=0, second=0, interval=3)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1973, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1976, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1979, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp(),
        ])

    def test_with_time(self):
        time_controller = TestTimeController()
        events = []
        clocks = []
        def action():
            if len(clocks) >= 2:
                events[0].cancel()
            clocks.append(time_controller.get_clock())
        scheduler = CalendarScheduler(timefunc=time_controller.get_clock, sleep_controller=time_controller)
        start_time = datetime.datetime(1970, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        event = scheduler.enter_yearly_event(action=action, tz=datetime.timezone.utc, start_time=start_time, month=2, day=10, hour=13, minute=14, second=15)
        events.append(event)
        scheduler.run()
        self.assertEqual(clocks, [
            datetime.datetime(1970, 2, 10, 13, 14, 15, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1971, 2, 10, 13, 14, 15, tzinfo=datetime.timezone.utc).timestamp(),
            datetime.datetime(1972, 2, 10, 13, 14, 15, tzinfo=datetime.timezone.utc).timestamp(),
        ])


class TestYearlyFirstTime(unittest.TestCase):
    def setUp(self):
        self.time_controller = TestTimeController()
        self.scheduler = CalendarScheduler(timefunc=self.time_controller.get_clock, sleep_controller=self.time_controller)
        self.event = None
        self.clock = None

    def action(self):
        self.event.cancel()
        self.clock = self.time_controller.get_clock()

    def test_first_occurrence_before(self):
        # Событие 5 января, стартуем 1 января 1970
        start = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_yearly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, month=1, day=5, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())

    def test_first_occurrence_at(self):
        # Событие 5 января, стартуем 5 января
        start = datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_yearly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, month=1, day=5, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())

    def test_first_occurrence_after(self):
        # Событие 5 января, стартуем 6 января (следующий год)
        start = datetime.datetime(1970, 1, 6, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_yearly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, month=1, day=5, hour=0, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1971, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())

    def test_with_time(self):
        # 5 января 12:34:56, стартуем 1 января
        start = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_yearly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, month=1, day=5, hour=12, minute=34, second=56)
        self.scheduler.run()
        expected = datetime.datetime(1970, 1, 5, 12, 34, 56, tzinfo=datetime.timezone.utc).timestamp()
        self.assertEqual(self.clock, expected)

    def test_interval_2_years(self):
        # 5 января, интервал 2 года, стартуем 1 января
        start = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
        self.event = self.scheduler.enter_yearly_event(action=self.action, tz=datetime.timezone.utc, start_time=start, month=1, day=5, hour=0, minute=0, second=0, interval=2)
        self.scheduler.run()
        self.assertEqual(self.clock, datetime.datetime(1970, 1, 5, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())


@unittest.skip("so long")
class TestRealDaily(unittest.TestCase):
    def test_once(self):
        events = []

        def action():
            print(datetime.datetime.now())
            events[0].cancel()

        scheduler = CalendarScheduler()
        event = scheduler.enter_daily_event(action=action, hour=18, minute=30, second=30)
        events.append(event)
        scheduler.run()


#TODO:
# Передача в action args и kwargs
# тесты на границы interval, second, minute и так далее
# тесты с более реальным временем, начинающимся не с нуля
# тесты реального времени на одно исполнение на основе текущего времени, просто подбираем параметры запуска ближайщие к текущему времени
# при пропуске события, запуск по сетке.
# тест перехода через новый год 1970

if __name__ == '__main__':
    # TODO: сделать прерывание по таймауту, так как тест может зависнуть.
    unittest.main()
