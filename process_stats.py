#!/usr/bin/env python3

import os
import statistics
import sys
import datetime
from pathlib import Path

from typing import List

from buildstats import Build, Sync


def total_time(builds):
    all_times = (b.time_taken_in_seconds() for b in builds)
    return sum(all_times)


def total_time_excluding_clean(builds):
    all_times = (b.time_taken_in_seconds() for b in builds if b.tasks != 'clean')
    return sum(all_times)


def total_build_count(builds):
    return len(builds)


def total_build_count_excluding_clean(builds):
    return len([b for b in builds if b.tasks != 'clean'])


def median_build_time(builds):
    all_times = (b.time_taken_in_seconds() for b in builds)
    return statistics.median(all_times)


def median_build_time_excluding_clean(builds):
    all_times = (b.time_taken_in_seconds() for b in builds if b.tasks != 'clean')
    return statistics.median(all_times)


def deduplicate(builds):
    return list(set(builds))


def remove_clean_builds(builds):
    return (b for b in builds if b.tasks != 'clean')


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
    for build in sorted(all_builds, key=lambda x: x.when):
        output_csv.write(build.to_csv())
        output_csv.write("\n")


def output_filename(user=None, date=None):
    user = user or os.getlogin()
    date = date or datetime.date.today()
    return f"{date.isoformat()}-{user}.csv"


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
        gather_builds(folder, f)


if __name__ == "__main__":
    main(sys.argv[1:])
