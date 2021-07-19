from datetime import timedelta

def parse_to_secs(raw_time):
	secs = 0
	mins = 0
	hours = 0
	fields = [x.strip() for x in raw_time.strip().split()]
	if fields and fields[-1] == 'ms':
		fields = fields[:-2] # ignore ms fields
	if fields and fields[-1] == 's':
		secs = int(fields[-2])
		fields = fields[:-2]
	if fields and fields[-1] == 'm':
		mins = int(fields[-2])
		fields = fields[:-2]
	if fields and fields[-1] == 'h':
		hours = int(fields[-2])
	t = timedelta(hours=hours, minutes=mins, seconds=secs)
	return t.total_seconds()


def total_time(builds):
	all_times = (parse_to_secs(b.time_taken) for b in builds)
	return sum(all_times)

