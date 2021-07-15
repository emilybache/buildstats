#!/usr/bin/env python3

import datetime
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Build:
    """Contains the raw data from the log parsed into string fields, no further processing"""
    when: str
    time_taken: str
    outcome: str
    tasks: str


@dataclass
class NamedRegex:
    regex: re.Pattern
    name: str


GRADLE_BUILD_RE = re.compile(r"^([\d\-:,\s]+) \[\d+\].* Gradle build (\w+) in ([\d\s\w]+)\n$")
GRADLE_TASKS_RE = re.compile(r"^.* About to execute Gradle tasks: \[([\w\s,:-]+)\].*$")


def next_match(lines, regexes):
    for line in lines:
        for named_regex in regexes:
            match = named_regex.regex.match(line)
            if match:
                yield named_regex.name, match


def task_list(tasks):
    tasks = tasks.split(", ")
    if tasks == [""]:
        return []
    return tasks


def next_build(matches):
    tasks = ""
    for name, match in matches:
        if name == "tasks":
            tasks = match.group(1)
        if name == "build":
            when = match.group(1)
            outcome = match.group(2)
            time_taken = match.group(3)
            yield Build(when=when, outcome=outcome, time_taken=time_taken, tasks=tasks)
            tasks = "" # reset tasks in case we get another build before another tasks


def filter_gradle_builds(lines):
    matches = next_match(lines, [NamedRegex(GRADLE_BUILD_RE, "build"), NamedRegex(GRADLE_TASKS_RE, "tasks")])
    builds = (build for build in next_build(matches))
    return builds


def output_filename(user=None, date=None):
    user = user or os.getlogin()
    date = date or datetime.date.today()
    return f"{date.isoformat()}-{user}.log"


def parse_builds(idea_log, output):
    for build in filter_gradle_builds(idea_log):
        output.write(f"{build}\n")


def main(log_file, output_filename):
    with open(log_file) as f:
        with open(output_filename, "w") as output_file:
            parse_builds(f, output_file)


def guess_path_to_idea_log():
    possible_paths = [
        Path.home() / "Library/Logs/Google/AndroidStudio4.2/idea.log",
        Path.home() / "Library/Logs/Google/AndroidStudio4.1/idea.log",
    ]
    for p in possible_paths:
        if p.exists():
            return p
    return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = guess_path_to_idea_log()
    if not path:
        print("unable to locate 'idea.log'! You can find it in your JetBrains IDE on the 'help' menu - 'Show log in Finder'. You should give the full path to idea.log as an argument to this script.")
        sys.exit(1)
    else:
        output = output_filename()
        print(f"Will parse log file {path} and write builds to {output}")
        main(path, output)