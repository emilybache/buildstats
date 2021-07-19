from process_stats import *
from buildstats import Build


def test_parse_to_secs():
	assert parse_to_secs('252 ms ') == 0
	assert parse_to_secs('17 s 252 ms ') == 17
	assert parse_to_secs('2 m 17 s 252 ms ') == 137

def test_total_time():
	builds = [
	Build(when='2021-07-16 12:31:45,195', time_taken='2 m 22 s 428 ms ', outcome='finished', tasks=':app:assemble'),
	Build(when='2021-07-16 13:33:31,933', time_taken='2 m 17 s 252 ms ', outcome='finished', tasks=':app:assemble'),
	]

	assert total_time(builds) == 279
