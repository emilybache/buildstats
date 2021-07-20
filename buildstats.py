#!/usr/bin/env python3

import datetime
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, order=True)
class Build:
    """Contains the raw test_data from the log parsed into string fields,
    with methods to extract the processed test_data in more convenient formats"""
    when: str
    time_taken: str
    outcome: str
    tasks: str

    def to_csv(self):
        return f"{self.when}, {self.time_taken_in_seconds()}, {self.outcome}, {self.tasks}"

    def time_taken_in_seconds(self):
        return parse_to_secs(self.time_taken)


def parse_to_secs(raw_time):
    ms = 0
    secs = 0
    mins = 0
    hours = 0
    fields = [x.strip() for x in raw_time.strip().split()]
    if fields and fields[-1] == 'ms':
        ms = int(fields[-2])
        fields = fields[:-2]
    if fields and fields[-1] == 's':
        secs = int(fields[-2])
        fields = fields[:-2]
    if fields and fields[-1] == 'm':
        mins = int(fields[-2])
        fields = fields[:-2]
    if fields and fields[-1] == 'h':
        hours = int(fields[-2])
    t = datetime.timedelta(hours=hours, minutes=mins, seconds=secs, milliseconds=ms)
    return t.total_seconds()


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


def parse_idea_log(log_file, output_filename):
    with open(log_file) as f:
        with open(output_filename, "a") as output_file:
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


def main(args):
    """
    Process the file created by the IDE into a log of builds,
    which it will put in the folder 'testdata'.
    By default it will look for the idea.log file in the default places for Android Studio versions 4.2 and 4.1.
    Pass an argument to look in a different place instead
    """
    if args:
        path = args[0]
    else:
        path = guess_path_to_idea_log()
    if not path:
        print(
            "unable to locate 'idea.log'! You can find it in your JetBrains IDE on the 'help' menu - 'Show log in Finder'. You should give the full path to idea.log as an argument to this script.")
        return

    data_folder = Path.cwd() / "testdata"
    if not data_folder.exists():
        os.mkdir(data_folder)
    output = data_folder / output_filename()
    print(f"Will parse log file {path} and write builds to {output}")
    parse_idea_log(path, output)


if __name__ == '__main__':
    main(sys.argv[1:])