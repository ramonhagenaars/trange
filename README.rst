|PyPI version| |Build Status|

trange
======

A *very lightweight* Python lib for ``datetime`` ranges.


Installation
''''''''''''

::

   pip install trange

Usage
'''''

.. code:: python

   from trange import trange

   trange(datetime_1200, datetime_1300)  # Two datetime objects


Once created, you can iterate through a ``TimeRange`` using a generator:

.. code:: python

   for dt in trange1.step(minutes=15):
       print('This is printed every 15 minutes within trange1.')


There are many other ways to create a ``TimeRange`` instance:

.. code:: python

   trange1 = trange(datetime_1200, timedelta(hours=1))  # A datetime and a timedelta
   trange2 = trange(datetime_1200)                      # A TimeRange that does not end
   trange3 = trange()                                   # A TimeRange from now to eternity
   trange4 = trange(timedelta(hours=1))                 # A TimeRange that starts in 1 hour to eternity
   trange5 = trange(datetime_1300, datetime_1200)       # A backward TimeRange
   trange6 = trange(end=datetime_1200)                  # A backward TimeRange until datetime_1200


You can even use two ``timedelta`` instances:

.. code:: python

   # This range will start in 1 hour and end 1 hour later than start (so in 2 hours):
   trange6 = trange(timedelta(hours=1), timedelta(hours=1)


Iterating through a backward ``TimeRange`` instance works as well:

.. code:: python

   for dt in trange5.step(minutes=15):
       print("We're going back in time with steps of 15 minutes.")


You can check if some ``datetime`` is withing the range:

.. code:: python

   if datetime_1230 in trange1:
       print('Yes, it is in range!')

Detailed information
''''''''''''''''''''
You can create a ``TimeRange`` by providing two ``datetime`` instances:

::

    trange(datetime_1230, datetime_1415)

                    |------------------------->>|
    __.______.______.______.______.______.______.______.______.______.__
    12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00

|
|

If the date and time of the first ``datetime`` is later than the second, a ``BackwardTimeRange`` is returned:

::

    trange(datetime_1415, datetime_1230)

                    |<<=========================|
    __.______.______.______.______.______.______.______.______.______.__
    12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00

|
|

The second parameter can be omitted, in which case an infinite ``TimeRange`` instance is created:

::

    trange(datetime_1230)

                    |=============================================== ...
    __.______.______.______.______.______.______.______.______.______.__
    12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00

|
|

If only ``end`` is provided, a ``TimeRange`` is created that defines a range 'until now'. This is a special case as a ``BackwardTimeRange`` is created that points infinitely back in history, starting at ``end``:

::

    trange(end=datetime_1400)

    ... =================================|
    __.______.______.______.______.______.______.______.______.______.__
    12:00  12:15  12:30  12:45  13:30  14:00  14:15  14:30  14:45  15:00

.. |PyPI version| image:: https://badge.fury.io/py/trange.svg
   :target: https://badge.fury.io/py/trange
.. |Build Status| image:: https://travis-ci.com/ramonhagenaars/trange.svg?branch=master
   :target: https://travis-ci.com/ramonhagenaars/trange
