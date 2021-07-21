import statistics


def total_time(builds):
    all_times = (b.time_taken_in_seconds() for b in builds)
    seconds = sum(all_times)
    return seconds


def total_build_count(builds):
    return len(builds)


def median_time(builds):
    all_times = [b.time_taken_in_seconds() for b in builds]
    if not all_times:
        return None
    median_time = statistics.median(all_times)
    return median_time


def pretty_print_timedelta(seconds):
    if not seconds:
        return ""
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    milliseconds = round((seconds % 1) * 1000)
    if days > 0:
        return '%d d %d h %d m %d s %d ms' % (days, hours, minutes, seconds, milliseconds)
    elif hours > 0:
        return '%d h %d m %d s %d ms' % (hours, minutes, seconds, milliseconds)
    elif minutes > 0:
        return '%d m %d s %d ms' % (minutes, seconds, milliseconds)
    elif seconds >= 1:
        return '%d s %d ms' % (seconds, milliseconds)
    else:
        return '%d ms' % (milliseconds)


def summary_statistics(builds):
    builds_excluding_clean = [b for b in builds if not b.is_a_clean() and not b.is_a_sync()]
    syncs = [b for b in builds if b.is_a_sync()]
    summary = f"""
Builds (excluding 'clean')
----------------------------------
Total number: {total_build_count(builds_excluding_clean)}
Total time: {pretty_print_timedelta(total_time(builds_excluding_clean))}
Median time: {pretty_print_timedelta(median_time(builds_excluding_clean))}

Syncs
------
Total number: {total_build_count(syncs)}
Total time: {pretty_print_timedelta(total_time(syncs))}
Median time: {pretty_print_timedelta(median_time(syncs))}

All builds and syncs
--------------------
Total number: {total_build_count(builds)}
Total time: {pretty_print_timedelta(total_time(builds))}
Median time: {pretty_print_timedelta(median_time(builds))}
"""
    return summary


def remove_clean_builds(builds):
    return (b for b in builds if b.is_a_clean_or_sync())