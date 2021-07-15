Build Stats
===========

We might like to keep track of how long we spend waiting for the build. 
This script assumes you're using a tool like Android Studio which produces a log.
It uses regular expressions to pick out interesting entries from the log.
It can produce a list of "Build" objects that you can use to gather statistics.

Soon I will develop code that can parse a list of Build objects and give you some statistics.

Usage
-----

    $ buildstats.py /path/to/idea.log

Tests
-----
The self-tests use [pytest](https://docs.pytest.org/).