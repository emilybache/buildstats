import pytest
from approvaltests import verify

from calculate_statistics import total_time, total_build_count, median_time, summary_statistics, pretty_print_timedelta
from test_process_to_csv import SAMPLE_BUILDS, SAMPLE_BUILDS_2, SAMPLE_BUILDS_3

from gather_build_data import Build


def test_total_time():
    assert total_time(SAMPLE_BUILDS) == pytest.approx(523.69, 0.1)


def test_total_build_count():
    assert total_build_count(SAMPLE_BUILDS) == 4


def test_median_time():
    assert median_time(SAMPLE_BUILDS) == pytest.approx(139.84, 0.1)


def test_summary_stats():
    stats = summary_statistics(SAMPLE_BUILDS + SAMPLE_BUILDS_2 + SAMPLE_BUILDS_3)

    verify(stats)


def test_pretty_print_timedelta():
    build = Build(when='2021-07-16 12:31:45,195', time_taken='2 m 22 s 428 ms ', outcome='finished', tasks=':app:assemble')
    assert pretty_print_timedelta(build.time_taken_in_seconds()) == '2 m 22 s 428 ms'

    build = Build(when='2021-07-16 12:31:45,195', time_taken='428 ms ', outcome='finished',
                  tasks=':app:assemble')
    assert pretty_print_timedelta(build.time_taken_in_seconds()) == '428 ms'