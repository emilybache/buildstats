import os
import statistics

from typing import List

from buildstats import Build


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


def deduplicate(builds: List[Build]):
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
            pass
    return all_builds


def gather_builds(folder, output_csv):
    for root, directories, files in os.walk(folder):
        for file in files:
            if file.endswith(".log"):
                with open(os.path.join(root, file)) as log_file:
                    builds = gather_builds_from(log_file)
                    builds = deduplicate(builds)
                    for build in sorted(builds):
                        output_csv.write(build.to_csv())
                        output_csv.write("\n")

