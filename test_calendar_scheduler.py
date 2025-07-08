import datetime
import unittest
import time

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

        # TODO: должен начинаться с 0.0
        self.assertEqual(clocks, [1.0, 2.0, 3.0, 4.0, 5.0])

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

        self.assertEqual(clocks, [2.0, 4.0, 6.0])


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
        event = scheduler.enter_hourly_event(action=action)
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
        self.event = self.scheduler.enter_hourly_event(action=self.action, start_time=59, minute=1, second=0)
        self.scheduler.run()
        self.assertEqual(60.0, self.clock)

    def test_2(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, start_time=65, minute=1, second=5)
        self.scheduler.run()
        self.assertEqual(65.0, self.clock)

    def test_3(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, start_time=65, minute=1, second=6)
        self.scheduler.run()
        self.assertEqual(66.0, self.clock)

    def test_4(self):
        self.event = self.scheduler.enter_hourly_event(action=self.action, start_time=65, minute=1, second=4)
        self.scheduler.run()
        self.assertEqual(3664.0, self.clock)


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
        event = scheduler.enter_daily_event(action=action)
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
        self.event = self.scheduler.enter_daily_event(action=self.action, start_time=3600, hour=2, minute=1, second=1)
        self.scheduler.run()
        self.assertEqual(7261, self.clock)

    def test_2(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, start_time=3660, hour=1, minute=2, second=1)
        self.scheduler.run()
        self.assertEqual(3721, self.clock)

    def test_3(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, start_time=3661, hour=1, minute=1, second=2)
        self.scheduler.run()
        self.assertEqual(3662, self.clock)

    def test_4(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, start_time=3662, hour=1, minute=1, second=2)
        self.scheduler.run()
        self.assertEqual(3662, self.clock)

    def test_5(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, start_time=3662, hour=1, minute=1, second=1)
        self.scheduler.run()
        self.assertEqual(90061, self.clock)

    def test_6(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, start_time=3662, hour=1, minute=0, second=1)
        self.scheduler.run()
        self.assertEqual(90001, self.clock)

    def test_7(self):
        self.event = self.scheduler.enter_daily_event(action=self.action, start_time=7200, hour=1, minute=0, second=0)
        self.scheduler.run()
        self.assertEqual(90000, self.clock)


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


#TODO:
# Передача в action args и kwargs
# тесты на границы interval, second, minute и так далее
# тесты с более реальным временем, начинающимся не с нуля
# тесты реального времени на одно исполнение на основе текущего времени, просто подбираем параметры запуска ближайщие к текущему времени


if __name__ == '__main__':
    # TODO: сделать прерывание по таймауту, так как тест может зависнуть.
    unittest.main()
