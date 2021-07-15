#!/usr/bin/env python3

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Build:
    when: str
    time_taken: str
    outcome: str
    tasks: str


@dataclass
class Matcher:
    regex: re.Pattern
    name: str


gradle_build_pattern = r"^([\d\-:,\s]+) \[\d+\].* Gradle build (\w+) in ([\d\s\w]+)\n$"
gradle_task_pattern = r"^.* About to execute Gradle tasks: \[([\w\s,:]+)\].*$"


def next_match(lines, regexes):
    for line in lines:
        regex = regexes[0].regex
        match = regex.match(line)
        if match:
            yield regexes[0].name, match


def next_build(matches):
    for name, match in matches:
        if name == "build":
            when = match.group(1)
            outcome = match.group(2)
            time_taken = match.group(3)
            yield Build(when=when, outcome=outcome, time_taken=time_taken, tasks="")


def filter_gradle_builds(lines):
    regex = re.compile(gradle_build_pattern)

    matches = next_match(lines, [Matcher(regex, "build")])
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
