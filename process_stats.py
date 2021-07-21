#!/usr/bin/env python3
import math
import os
import statistics
import sys
import datetime
from pathlib import Path

from buildstats import Build, Sync


def total_time(builds):
    all_times = (b.time_taken_in_seconds() for b in builds)
    seconds = sum(all_times)
    return seconds


def total_build_count(builds):
    return len(builds)


def median_time(builds):
    all_times = (b.time_taken_in_seconds() for b in builds)
    median_time = statistics.median(all_times)
    return median_time


def deduplicate(builds):
    return list(set(builds))


def remove_clean_builds(builds):
    return (b for b in builds if b.is_a_clean_or_sync())


def gather_builds_from(f):
    all_builds = []
    for line in f:
        try:
            b = eval(line)
            all_builds.append(b)
        except NameError as e:
            print("Error gathering builds: ", e)
    return all_builds


def gather_builds(folder, output_csv):
    all_builds = []
    for root, directories, files in os.walk(folder):
        for file in files:
            if file.endswith(".log"):
                with open(os.path.join(root, file)) as log_file:
                    builds = gather_builds_from(log_file)
                    builds = deduplicate(builds)
                    all_builds.extend(builds)
    sorted_builds = sorted(all_builds, key=lambda x: x.when)
    for build in sorted_builds:
        output_csv.write(build.to_csv())
        output_csv.write("\n")
    return sorted_builds


def output_filename(user=None, date=None):
    user = user or os.getlogin()
    date = date or datetime.date.today()
    return f"{date.isoformat()}-{user}.csv"


def pretty_print_timedelta(seconds):
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


def main(args):
    """Process the log files created by the 'buildstats' script into a csv file,
    which it will put in the folder 'processed_data'.
    By default it will look for the log files in the folder 'data'.
    Pass an argument to look in a different folder instead"""
    if args:
        folder = args[0]
    else:
        folder = Path.cwd() / "data"
    processed_data_folder = Path.cwd() / "processed_data"
    if not processed_data_folder.exists():
        os.mkdir(processed_data_folder)
    output_path = processed_data_folder / output_filename()
    print(f"Will parse log files found under {folder} and write a csv file to {processed_data_folder}")
    with open(output_path, "w") as f:
        builds = gather_builds(folder, f)
        
    stats = summary_statistics(builds)
    sys.stdout.write(stats)


if __name__ == "__main__":
    main(sys.argv[1:])
