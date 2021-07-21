#!/usr/bin/env python3
import os
import sys
import datetime
from pathlib import Path

from gather_build_data import Build, Sync

from calculate_statistics import summary_statistics


def deduplicate(builds):
    return list(set(builds))


def gather_builds_from(f):
    all_builds = []
    for line in f:
        try:
            # This will fail if you havn't imported Build and Sync classes in this file
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
