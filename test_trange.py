from datetime import datetime, timedelta
from unittest import TestCase
from trange import trange, ForwardTimeRange, BackwardTimeRange


class TestTRange(TestCase):

    def test_simple(self):
        d1 = datetime(year=2019, month=1, day=1, hour=12, minute=0, second=0,
                      microsecond=0)
        d2 = datetime(year=2019, month=1, day=2, hour=12, minute=0, second=0,
                      microsecond=0)

        # start: datetime, end: datetime, forward
        self.assertEqual(trange(d1, d2), ForwardTimeRange(d1, d2))

        # start: datetime, end: datetime, backward
        self.assertEqual(trange(d2, d1), BackwardTimeRange(d2, d1))

        # start: datetime, end: timedelta, forward
        self.assertEqual(trange(d1, timedelta(days=1)), ForwardTimeRange(d1, d2))

        # start: datetime, end: timedelta, backward
        self.assertEqual(trange(d2, timedelta(days=-1)), BackwardTimeRange(d2, d1))

        # start: datetime, end: None, forward
        self.assertEqual(trange(d1), ForwardTimeRange(d1))

        # start: None, end: datetime, backward
        self.assertEqual(trange(end=d1), BackwardTimeRange(d1))

        now = datetime.now()
        td = timedelta(hours=1)

        # start: timedelta, end: None, forward
        tr1 = trange(td)
        self.assertTrue(isinstance(tr1, ForwardTimeRange))
        self.assertEqual(tr1.end, None)
        self.assertEqual((now.hour + 1, now.minute, now.second),
                         (tr1.start.hour, tr1.start.minute, tr1.start.second))

        # start: None, end: timedelta, backward
        tr2 = trange(end=td)
        self.assertTrue(isinstance(tr2, BackwardTimeRange))
        self.assertEqual(tr2.end, None)
        self.assertEqual((now.hour + 1, now.minute, now.second),
                         (tr2.start.hour, tr2.start.minute, tr2.start.second))

        # start: timedelta, end: timedelta, forward
        tr3 = trange(timedelta(hours=1), timedelta(hours=1))
        self.assertTrue(isinstance(tr3, ForwardTimeRange))
        self.assertEqual((now.hour + 1, now.minute, now.second),
                         (tr3.start.hour, tr3.start.minute, tr3.start.second))
        self.assertEqual((tr3.start.hour + 1, tr3.start.minute, tr3.start.second),
                         (tr3.end.hour, tr3.end.minute, tr3.end.second))

        # start: timedelta, end: timedelta, backward
        tr3 = trange(timedelta(hours=1), timedelta(hours=-1))
        self.assertTrue(isinstance(tr3, BackwardTimeRange))
        self.assertEqual((now.hour + 1, now.minute, now.second),
                         (tr3.start.hour, tr3.start.minute, tr3.start.second))
        self.assertEqual((tr3.start.hour - 1, tr3.start.minute, tr3.start.second),
                         (tr3.end.hour, tr3.end.minute, tr3.end.second))

    def test_wrong_dates(self):
        d1 = datetime(year=2019, month=1, day=1, hour=12, minute=0, second=0,
                      microsecond=0)
        d2 = datetime(year=2019, month=1, day=2, hour=12, minute=0, second=0,
                      microsecond=0)

        with self.assertRaises(ValueError):
            ForwardTimeRange(d2, d1)
        with self.assertRaises(ValueError):
            BackwardTimeRange(d1, d2)

    def test_steps(self):
        d1 = datetime(year=2019, month=1, day=1, hour=12, minute=0, second=0,
                      microsecond=0)
        d2 = datetime(year=2019, month=1, day=2, hour=12, minute=0, second=0,
                      microsecond=0)

        # Forward.
        tr1 = trange(d1, d2)
        self.assertEqual(25, len(list(tr1.steps(delta=timedelta(hours=1)))))
        self.assertEqual(25, len(list(tr1.steps(hours=1))))
        self.assertEqual(2, len(list(tr1.steps(hours=24))))
        self.assertEqual(24, len(list(tr1.steps(hours=1, include_end=False))))
        self.assertEqual(23, len(list(tr1.steps(hours=1, include_start=False,
                                                include_end=False))))

        # Backward.
        tr2 = trange(d2, d1)
        self.assertEqual(25, len(list(tr2.steps(delta=timedelta(hours=1)))))
        self.assertEqual(25, len(list(tr2.steps(hours=1))))
        self.assertEqual(2, len(list(tr2.steps(hours=24))))
        self.assertEqual(24, len(list(tr2.steps(hours=1, include_end=False))))
        self.assertEqual(23, len(list(tr2.steps(hours=1, include_start=False,
                                                include_end=False))))

        with self.assertRaises(TypeError):
            for _ in tr1.steps(delta='silly walk'):
                print('Never reached')

    def test_delta(self):
        d1 = datetime(year=2019, month=1, day=1, hour=12, minute=0, second=0,
                      microsecond=0)
        d2 = datetime(year=2019, month=1, day=2, hour=12, minute=0, second=0,
                      microsecond=0)
        self.assertEqual(timedelta(days=1), trange(d1, d2).delta)
        self.assertEqual(timedelta(days=-1), trange(d2, d1).delta)

    def test_eq(self):
        d1 = datetime(year=2019, month=1, day=1, hour=12, minute=0, second=0,
                      microsecond=0)
        d2 = datetime(year=2019, month=1, day=2, hour=12, minute=0, second=0,
                      microsecond=0)
        self.assertTrue(trange(d1, d2) == trange(d1, d2))
        self.assertTrue(trange(d2, d1) == trange(d2, d1))
        self.assertTrue(trange(d1, d2) != trange(d2, d1))

    def test_contains(self):
        d1 = datetime(year=2019, month=1, day=1, hour=12, minute=0, second=0,
                      microsecond=0)
        d2 = datetime(year=2020, month=1, day=1, hour=12, minute=0,
                      second=0, microsecond=0)
        d3 = datetime(year=2021, month=1, day=1, hour=12, minute=0, second=0,
                      microsecond=0)
        tr1f = trange(d1, d3)
        tr2f = trange(d1, d2)
        tr3f = trange(d2, d3)
        self.assertTrue(d2 in tr1f)
        self.assertTrue(d2 in tr2f)
        self.assertTrue(d2 in tr3f)

        tr1b = trange(d3, d1)
        tr2b = trange(d2, d1)
        tr3b = trange(d3, d2)
        self.assertTrue(d2 in tr1b)
        self.assertTrue(d2 in tr2b)
        self.assertTrue(d2 in tr3b)
        with self.assertRaises(TypeError):
            'Chuck Norris' in tr1f  # Ha! Chuck Norris fits in no range!

    def test_repr(self):
        # Check if repr returns a string that shows exactly how to create a
        # replica.
        import datetime
        d1 = datetime.datetime(year=2019, month=1, day=1, hour=12, minute=0,
                               second=0, microsecond=0)
        d2 = datetime.datetime(year=2019, month=1, day=2, hour=12, minute=0,
                               second=0, microsecond=0)
        trf = trange(d1, d2)
        trf_str = repr(trf)
        self.assertTrue(trf == eval(trf_str))

        trb = trange(d2, d1)
        trb_str = repr(trb)
        self.assertTrue(trb == eval(trb_str))
