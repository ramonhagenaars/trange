"""
Contains the ``TimeRange``, ``ForwardTimeRange`` and ``BackwardTimeRange``
classes and the ``trange`` function that can be used to created instances of
these classes.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


def trange(start=None, end=None):
    """
    Return a ``TimeRange`` instance depending on ``start`` and ``end``. The
    parameters can be of type ``datetime.datetime`` or ``datetime.timedelta``.

    |
    |
    | You can create a ``TimeRange`` by providing two ``datetime`` instances:
    |
    | ``trange(datetime_1230, datetime_1415)``
    |
    |                 |=========================>>|
    | __.______.______.______.______.______.______.______.______.______.__
    | 12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00
    |
    |
    |
    | If the date and time of the first ``datetime`` is later than the second,
    | a ``BackwardTimeRange`` is returned:
    |
    | ``trange(datetime_1415, datetime_1230)``
    |
    |                 |<<=========================|
    | __.______.______.______.______.______.______.______.______.______.__
    | 12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00
    |
    |
    |
    | The second parameter can be omitted, in which case an infinite
    | ``TimeRange`` instance is created:
    |
    | ``trange(datetime_1230)``
    |
    |                 |=============================================>> ...
    | __.______.______.______.______.______.______.______.______.______.__
    | 12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00
    |
    |
    |
    | If only ``end`` is provided, a ``TimeRange`` is created that represents
    | 'until now'. This is a special case as a ``BackwardTimeRange`` is created
    | that points infinitely back in history, starting at ``end``.
    |
    | ``trange(end=datetime_1400)``
    |
    | ... <<===============================|
    | __.______.______.______.______.______.______.______.______.______.__
    | 12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00
    |

    :param start: a ``datetime`` or ``timedelta`` that defines the start of the
    range.
    :param end: a ``datetime`` or ``timedelta`` that defines the end of the
    range.
    :return: a ``TimeRange`` instance that can be a ``ForwardTimeRange`` or a
    ``BackwardTimeRange``.
    """
    start_ = datetime.now()
    end_ = None
    cls = ForwardTimeRange
    if start:
        _check_type('start', start, datetime, timedelta)
        start_ = (start_ + start if isinstance(start, timedelta)
                  else start)
        if end:
            _check_type('end', end, datetime, timedelta)
            end_ = start_ + end if isinstance(end, timedelta) else end
            cls = ForwardTimeRange if start_ <= end_ else BackwardTimeRange
    else:
        if end:
            _check_type('end', end, datetime, timedelta)
            start_ = (start_ + end if isinstance(end, timedelta)
                      else end)
            cls = BackwardTimeRange
    return cls(start_, end_)


class TimeRange(ABC):
    """
    An abstract class that defines a range of time. A ``TimeRange`` can have
    two ends or only one end. In the latter case, the instance ranges to
    infinity.

    A ``TimeRange`` always has a concrete ``start``. The direction of stepping
    through a ``TimeRange`` is always from ``start`` to ``end``.
    """
    def __init__(self, start, end=None):
        """
        Constructor.
        :param start: a datetime that marks the start of the range.
        :param end: an optional datetime that marks the end of the range.
        """
        self._start = start
        self._end = end
        self._hash = None

    def steps(self, *, delta=None, weeks=0, days=0, hours=0, minutes=0,
              seconds=0, milliseconds=0, microseconds=0, include_start=True,
              include_end=True):
        """
        Return a generator that allows you to iterate through steps of a given
        size.
        :param delta: a ``timedelta`` instance that defines the step size.
        :param weeks: the number of weeks of the step size.
        :param days: the number of days of the step size.
        :param hours: the number of hours of the step size.
        :param minutes: the number of minutes of the step size.
        :param seconds: the number of seconds of the step size.
        :param milliseconds: the number of milliseconds of the step size.
        :param microseconds: the number of microseconds of the step size.
        :param include_start: determines whether the ``start`` datetime is
        included in the iteration.
        :param include_end: determines whether the ``end`` datetime is included
        in the iteration.
        :return: a generator.
        """
        if delta and not isinstance(delta, timedelta):
            raise TypeError("argument 'delta' must be an instance of "
                            "datetime.timedelta, not %s"
                            % type(delta).__name__)
        delta_ = delta or timedelta(weeks=weeks,
                                    days=days,
                                    hours=hours,
                                    minutes=minutes,
                                    seconds=seconds,
                                    milliseconds=milliseconds,
                                    microseconds=microseconds)
        current_date = self.start
        if not include_start:
            current_date += delta_
        while not self.end or self.contains(current_date, True, include_end):
            yield current_date
            current_date += delta_

    @property
    def start(self):
        """
        Return the start ``datetime`` of this ``TimeRange``.
        :return: the start ``datetime``.
        """
        return self._start

    @property
    def end(self):
        """
        Return the end ``datetime`` of this ``TimeRange``.
        :return: the end ``datetime``.
        """
        return self._end

    @property
    def delta(self):
        """
        Return a ``timedelta`` instance that represents the difference between
        ``start`` and ``end`` of this ``TimeRange``. If ``end`` is ``None``,
        then ``None`` is returned.
        :return: the delta between ``start`` and ``end`` or ``None`` if this
        ``TimeRange`` is infinite.
        """
        return self.end - self.start if self.end else None

    def __hash__(self):
        """
        Return a unique hashcode for this instance.
        :return: a unique hashcode as ``int``.
        """
        if not self._hash:
            date_pattern = '%Y%m%d%H%M%S%f'
            start_h = self.start.strftime(date_pattern)
            end_h = self.end.strftime(date_pattern) if self.end else 20 * '0'
            self._hash = int('%s%s%s' % (hash(self.__class__), start_h, end_h))
        return self._hash

    def __eq__(self, other):
        """
        Return whether ``self == other``, which is the case if both ``start``
        and ``end`` are equal and if the direction of ``self`` and ``other``
        are equal.
        :param other: the right operand.
        :return: ``True`` in case of equality.
        """
        return hash(self) == hash(other)

    def __repr__(self):
        """
        Return a textual representation of this instance.
        :return: a repr of this object.
        """
        return '%s(%s, %s)' % (self.__class__.__name__, repr(self.start),
                               repr(self.end))

    def __contains__(self, item):
        """
        Return whether ``item`` is in this ``TimeRange``, with both ``start``
        and ``end`` included. The parameter ``item`` can be of type
        ``datetime`` or ``TimeRange``.
        :param item: a ``datetime`` or ``TimeRange``.
        :return: ``True`` if ``item`` is in self.
        """
        return self.contains(item, True, True)

    @abstractmethod
    def __str__(self):
        """
        Return this instance as a string.
        :return: this instance as a string.
        """

    @abstractmethod
    def contains(self, item, include_start, include_end):
        """
        Return whether ``item`` is in this ``TimeRange``. The parameter
        ``item`` can be of type ``datetime`` or ``TimeRange``.
        :param item: a ``datetime`` or ``TimeRange``.
        :param include_start: determines whether item can be equal to
        ``start`` (``True``) or not (``False``).
        :param include_end: determines whether item can be equal to
        ``end`` (``True``) or not (``False``).
        :return: ``True`` if ``item`` is in self.
        """


class ForwardTimeRange(TimeRange):
    """
    A ``TimeRange`` implementation of which ``start >= end``.
    """
    def __init__(self, start, end=None):
        """
        Constructor.
        :param start: the ``datetime`` that specifies the start of this range.
        :param end: the ``datetime`` that specifies the end of this range. It
        must be equal to or later than ``start``.
        """
        _check_type('start', start, datetime)
        end and _check_type('end', end, datetime)
        if end and start > end:
            raise ValueError('A ForwardTimeRange does not allow start to be '
                             'greater than end, use BackwardTimeRange instead'
                             '.')
        TimeRange.__init__(self, start, end)

    def contains(self, item, include_start, include_end):
        """
        See ``TimeRange.contains``.
        :param item: See ``TimeRange.contains``.
        :param include_start: See ``TimeRange.contains``.
        :param include_end: See ``TimeRange.contains``.
        :return: See ``TimeRange.contains``.
        """
        after_start = ((include_start and item >= self.start)
                       or item > self.start)
        if self.end:
            before_end = ((include_end and item <= self.end)
                          or item < self.end)
        else:
            before_end = True # Infinite end
        return after_start and before_end

    def __str__(self):
        """
        Return this instance as string.
        :return: this instance in string format.
        """
        if self.end:
            return '[%s, ..., %s>' % (self.start, self.end)
        return '[%s, ...>' % self.start


class BackwardTimeRange(TimeRange):
    """
    A ``TimeRange`` implementation of which ``start < end``.
    """
    def __init__(self, start, end=None):
        """
        Constructor.
        :param start: the ``datetime`` that specifies the start of this range.
        :param end: the ``datetime`` that specifies the end of this range. It
        must be earlier than ``start``.
        """
        _check_type('start', start, datetime)
        end and _check_type('end', end, datetime)
        if end and start <= end:
            raise ValueError('A BackwardTimeRange does not allow start to be '
                             'lesser than or equal to end, use '
                             'ForwardTimeRange instead.')
        TimeRange.__init__(self, start, end)

    def steps(self, *, delta=None, weeks=0, days=0, hours=0, minutes=0,
              seconds=0, milliseconds=0, microseconds=0, include_start=True,
              include_end=True):
        """
        Return a generator for iterating through this ``BackwardTimeRange``
        using steps of a given size.

        Be aware that steps are to be *positive* if the generator is to iterate
        from ``start`` to ``end``.

        See ``TimeRange.steps``.
        :param delta: See ``TimeRange.steps``.
        :param weeks: See ``TimeRange.steps``.
        :param days: See ``TimeRange.steps``.
        :param hours: See ``TimeRange.steps``.
        :param minutes: See ``TimeRange.steps``.
        :param seconds: See ``TimeRange.steps``.
        :param milliseconds: See ``TimeRange.steps``.
        :param microseconds: See ``TimeRange.steps``.
        :param include_start: See ``TimeRange.steps``.
        :param include_end: See ``TimeRange.steps``.
        :return: See ``TimeRange.steps``.
        """
        if delta:
            _check_type('delta', delta, timedelta)
            delta = timedelta(seconds=delta.total_seconds() * -1)
        return TimeRange.steps(self, delta=delta, weeks=weeks * -1,
                               days=days * -1, hours=hours * -1,
                               minutes=minutes * -1, seconds=seconds * -1,
                               milliseconds=milliseconds * -1,
                               microseconds=microseconds * -1,
                               include_start=include_start,
                               include_end=include_end)

    def contains(self, item, include_start, include_end):
        """
        See ``TimeRange.contains``.
        :param item: See ``TimeRange.contains``.
        :param include_start: See ``TimeRange.contains``.
        :param include_end: See ``TimeRange.contains``.
        :return: See ``TimeRange.contains``.
        """
        before_start = ((include_start and item <= self.start)
                       or item < self.start)
        if self.end:
            after_end = ((include_end and item >= self.end)
                         or item > self.end)
        else:
            after_end = True # Infinite end
        return before_start and after_end

    def __str__(self):
        """
        Return this instance as string.
        :return: this instance in string format.
        """
        if self.end:
            return '<%s, ..., %s]' % (self.end, self.start)
        return '<..., %s]' % self.start


def _check_type(arg_name, arg, *types):
    # Check if the type of arg is in types. If not, raise a TypeError.
    for type_ in types:
        if isinstance(arg, type_):
            return
    str_types = [typ.__name__ for typ in types]
    raise TypeError("argument '%s' must be an instance of %s, not %s"
                    % (arg_name, ' or '.join(str_types), type(arg).__name__))
