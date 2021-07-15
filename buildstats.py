#!/usr/bin/env python3

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


def main(log_file):
    with open(log_file) as f:
        for build in filter_gradle_builds(f):
            print(build)


if __name__ == '__main__':
    path = Path.home() / "Library/Logs/Google/AndroidStudio4.2/idea.log"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    main(path)
