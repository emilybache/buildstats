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


def filter_gradle_builds(lines):
    gradle_build_pattern = r"^([\d\-:,\s]+) \[\d+\].* Gradle build (\w+) in ([\d\s\w]+)\n$"
    regex = re.compile(gradle_build_pattern)

    matches = (regex.match(line) for line in lines)
    return (Build(when=match.group(1), outcome=match.group(2), time_taken=match.group(3), tasks="")
                for match in matches if match)



def main(log_file):
    with open(log_file) as f:
        for build in filter_gradle_builds(f):
            print(build)


if __name__ == '__main__':
    path = Path.home() / "Library/Logs/Google/AndroidStudio4.2/idea.log"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    main(path)
